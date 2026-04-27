from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from auth import student_required
from database import query_db, execute_db
import json
import random
from datetime import datetime

student_bp = Blueprint('student', __name__)


@student_bp.route('/dashboard')
@student_required
def dashboard():
    exams = query_db('''
        SELECT e.*, u.full_name as creator_name,
               (SELECT COUNT(*) FROM questions WHERE exam_id = e.id) as question_count
        FROM exams e
        LEFT JOIN users u ON e.created_by = u.id
        WHERE e.is_active = 1
        ORDER BY e.created_at DESC
    ''')

    # Get exams already taken by this student
    taken_exam_ids = [r['exam_id'] for r in query_db(
        'SELECT exam_id FROM results WHERE user_id = ? AND is_submitted = 1', [current_user.id]
    )]

    return render_template('student/dashboard.html', exams=exams, taken_exam_ids=taken_exam_ids)


@student_bp.route('/exam/<int:exam_id>/start')
@student_required
def start_exam(exam_id):
    exam = query_db('SELECT * FROM exams WHERE id = ? AND is_active = 1', [exam_id], one=True)
    if not exam:
        flash('Exam not found or not available.', 'error')
        return redirect(url_for('student.dashboard'))

    # Check if already taken
    existing = query_db(
        'SELECT * FROM results WHERE user_id = ? AND exam_id = ? AND is_submitted = 1',
        [current_user.id, exam_id], one=True
    )
    if existing:
        flash('You have already completed this exam.', 'info')
        return redirect(url_for('student.view_result', result_id=existing['id']))

    # Check for in-progress attempt
    in_progress = query_db(
        'SELECT * FROM results WHERE user_id = ? AND exam_id = ? AND is_submitted = 0',
        [current_user.id, exam_id], one=True
    )

    if in_progress:
        result_id = in_progress['id']
    else:
        # Create new result record
        result_id = execute_db(
            'INSERT INTO results (user_id, exam_id, started_at) VALUES (?, ?, ?)',
            [current_user.id, exam_id, datetime.now().isoformat()]
        )

    # Get questions in random order (anti-cheating)
    questions = query_db(
        'SELECT id, question_text, option_a, option_b, option_c, option_d, marks FROM questions WHERE exam_id = ?',
        [exam_id]
    )
    questions = list(questions)
    random.shuffle(questions)

    # Store question order in session for this exam
    session[f'exam_{exam_id}_order'] = [q['id'] for q in questions]
    session[f'exam_{exam_id}_result'] = result_id

    return render_template('student/exam.html', exam=exam, questions=questions, result_id=result_id)


@student_bp.route('/exam/<int:exam_id>/submit', methods=['POST'])
@student_required
def submit_exam(exam_id):
    result_id = session.get(f'exam_{exam_id}_result')
    if not result_id:
        flash('Invalid exam session.', 'error')
        return redirect(url_for('student.dashboard'))

    result = query_db('SELECT * FROM results WHERE id = ? AND user_id = ?', [result_id, current_user.id], one=True)
    if not result or result['is_submitted']:
        flash('Exam already submitted or invalid.', 'error')
        return redirect(url_for('student.dashboard'))

    exam = query_db('SELECT * FROM exams WHERE id = ?', [exam_id], one=True)

    # Process answers
    data = request.get_json() if request.is_json else None
    answers = data.get('answers', {}) if data else {}

    questions = query_db('SELECT * FROM questions WHERE exam_id = ?', [exam_id])
    total_marks = 0
    score = 0

    for q in questions:
        qid = str(q['id'])
        selected = answers.get(qid, '')
        is_correct = 1 if selected == q['correct_option'] else 0
        if is_correct:
            score += q['marks']
        total_marks += q['marks']

        execute_db(
            'INSERT INTO answers (result_id, question_id, selected_option, is_correct) VALUES (?, ?, ?, ?)',
            [result_id, q['id'], selected, is_correct]
        )

    # Calculate time taken
    started = datetime.fromisoformat(result['started_at'])
    time_taken = int((datetime.now() - started).total_seconds())

    percentage = round((score / total_marks * 100), 1) if total_marks > 0 else 0

    execute_db('''
        UPDATE results SET score = ?, total_marks = ?, percentage = ?,
        submitted_at = ?, time_taken_seconds = ?, is_submitted = 1
        WHERE id = ?
    ''', [score, total_marks, percentage, datetime.now().isoformat(), time_taken, result_id])

    # Clear session
    session.pop(f'exam_{exam_id}_order', None)
    session.pop(f'exam_{exam_id}_result', None)

    return jsonify({'success': True, 'result_id': result_id})


@student_bp.route('/results')
@student_required
def results():
    results = query_db('''
        SELECT r.*, e.title as exam_title, e.department
        FROM results r
        JOIN exams e ON r.exam_id = e.id
        WHERE r.user_id = ? AND r.is_submitted = 1
        ORDER BY r.submitted_at DESC
    ''', [current_user.id])
    return render_template('student/results.html', results=results)


@student_bp.route('/result/<int:result_id>')
@student_required
def view_result(result_id):
    result = query_db('''
        SELECT r.*, e.title as exam_title, e.department, e.duration_minutes
        FROM results r
        JOIN exams e ON r.exam_id = e.id
        WHERE r.id = ? AND r.user_id = ?
    ''', [result_id, current_user.id], one=True)

    if not result:
        flash('Result not found.', 'error')
        return redirect(url_for('student.results'))

    answers = query_db('''
        SELECT a.*, q.question_text, q.option_a, q.option_b, q.option_c, q.option_d,
               q.correct_option, q.marks
        FROM answers a
        JOIN questions q ON a.question_id = q.id
        WHERE a.result_id = ?
    ''', [result_id])

    return render_template('student/result_detail.html', result=result, answers=answers)


@student_bp.route('/analytics')
@student_required
def analytics():
    """Course-wise performance analysis for the logged-in student."""
    # Get all results grouped by department/course
    course_stats = query_db('''
        SELECT e.department,
               COUNT(r.id) as exams_taken,
               COALESCE(ROUND(AVG(r.percentage), 1), 0) as avg_score,
               COALESCE(MAX(r.percentage), 0) as best_score,
               COALESCE(MIN(r.percentage), 0) as worst_score,
               SUM(CASE WHEN r.percentage >= 40 THEN 1 ELSE 0 END) as passed,
               SUM(CASE WHEN r.percentage < 40 THEN 1 ELSE 0 END) as failed
        FROM results r
        JOIN exams e ON r.exam_id = e.id
        WHERE r.user_id = ? AND r.is_submitted = 1
        GROUP BY e.department
        ORDER BY e.department
    ''', [current_user.id])

    # Get all individual results for the timeline
    all_results = query_db('''
        SELECT r.*, e.title as exam_title, e.department
        FROM results r
        JOIN exams e ON r.exam_id = e.id
        WHERE r.user_id = ? AND r.is_submitted = 1
        ORDER BY r.submitted_at DESC
    ''', [current_user.id])

    # Overall stats
    overall = query_db('''
        SELECT COUNT(r.id) as total_exams,
               COALESCE(ROUND(AVG(r.percentage), 1), 0) as avg_score,
               COALESCE(MAX(r.percentage), 0) as best_score,
               SUM(CASE WHEN r.percentage >= 40 THEN 1 ELSE 0 END) as passed
        FROM results r
        WHERE r.user_id = ? AND r.is_submitted = 1
    ''', [current_user.id], one=True)

    return render_template('student/analytics.html',
                           course_stats=course_stats,
                           all_results=all_results,
                           overall=overall)


@student_bp.route('/study-materials')
@student_required
def study_materials():
    """Browse study materials by course."""
    course_filter = request.args.get('course', '')

    if course_filter:
        materials = query_db('''
            SELECT sm.*, u.full_name as author_name
            FROM study_materials sm
            LEFT JOIN users u ON sm.created_by = u.id
            WHERE sm.course = ?
            ORDER BY sm.created_at DESC
        ''', [course_filter])
    else:
        materials = query_db('''
            SELECT sm.*, u.full_name as author_name
            FROM study_materials sm
            LEFT JOIN users u ON sm.created_by = u.id
            ORDER BY sm.created_at DESC
        ''')

    # Get unique courses for filter
    courses = query_db('SELECT DISTINCT course FROM study_materials ORDER BY course')

    return render_template('student/study_materials.html',
                           materials=materials,
                           courses=courses,
                           current_course=course_filter)


@student_bp.route('/study-materials/<int:material_id>')
@student_required
def view_material(material_id):
    """View a single study material."""
    material = query_db('''
        SELECT sm.*, u.full_name as author_name
        FROM study_materials sm
        LEFT JOIN users u ON sm.created_by = u.id
        WHERE sm.id = ?
    ''', [material_id], one=True)

    if not material:
        flash('Study material not found.', 'error')
        return redirect(url_for('student.study_materials'))

    return render_template('student/material_detail.html', material=material)
