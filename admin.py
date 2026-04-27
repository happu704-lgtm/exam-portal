from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from auth import admin_required
from database import query_db, execute_db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    stats = {
        'total_students': query_db('SELECT COUNT(*) as c FROM users WHERE role = "student"', one=True)['c'],
        'total_exams': query_db('SELECT COUNT(*) as c FROM exams', one=True)['c'],
        'active_exams': query_db('SELECT COUNT(*) as c FROM exams WHERE is_active = 1', one=True)['c'],
        'total_results': query_db('SELECT COUNT(*) as c FROM results WHERE is_submitted = 1', one=True)['c'],
        'avg_score': query_db('SELECT COALESCE(ROUND(AVG(percentage), 1), 0) as c FROM results WHERE is_submitted = 1', one=True)['c'],
        'total_questions': query_db('SELECT COUNT(*) as c FROM questions', one=True)['c'],
    }

    recent_results = query_db('''
        SELECT r.*, u.full_name, e.title as exam_title
        FROM results r
        JOIN users u ON r.user_id = u.id
        JOIN exams e ON r.exam_id = e.id
        WHERE r.is_submitted = 1
        ORDER BY r.submitted_at DESC LIMIT 10
    ''')

    return render_template('admin/dashboard.html', stats=stats, recent_results=recent_results)


@admin_bp.route('/exams')
@admin_required
def exams():
    exams = query_db('''
        SELECT e.*, u.full_name as creator_name,
               (SELECT COUNT(*) FROM questions WHERE exam_id = e.id) as question_count,
               (SELECT COUNT(*) FROM results WHERE exam_id = e.id AND is_submitted = 1) as attempt_count
        FROM exams e
        LEFT JOIN users u ON e.created_by = u.id
        ORDER BY e.created_at DESC
    ''')
    return render_template('admin/exams.html', exams=exams)


@admin_bp.route('/exam/create', methods=['GET', 'POST'])
@admin_required
def create_exam():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        department = request.form.get('department', '').strip()
        description = request.form.get('description', '').strip()
        duration = int(request.form.get('duration_minutes', 60))
        exam_type = request.form.get('exam_type', 'MCQ')
        deadline = request.form.get('deadline', '')
        notes = request.form.get('notes', '')
        image_url = request.form.get('image_url', '')

        if not title or not department:
            flash('Title and department are required.', 'error')
        else:
            exam_id = execute_db('''
                INSERT INTO exams (title, department, description, duration_minutes, exam_type,
                                   deadline, notes, image_url, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', [title, department, description, duration, exam_type, deadline, notes, image_url, current_user.id])
            flash('Exam created successfully!', 'success')
            return redirect(url_for('admin.manage_questions', exam_id=exam_id))

    return render_template('admin/exam_form.html', exam=None)


@admin_bp.route('/exam/<int:exam_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_exam(exam_id):
    exam = query_db('SELECT * FROM exams WHERE id = ?', [exam_id], one=True)
    if not exam:
        flash('Exam not found.', 'error')
        return redirect(url_for('admin.exams'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        department = request.form.get('department', '').strip()
        description = request.form.get('description', '').strip()
        duration = int(request.form.get('duration_minutes', 60))
        exam_type = request.form.get('exam_type', 'MCQ')
        is_active = 1 if request.form.get('is_active') else 0
        deadline = request.form.get('deadline', '')
        notes = request.form.get('notes', '')
        image_url = request.form.get('image_url', '')

        execute_db('''
            UPDATE exams SET title=?, department=?, description=?, duration_minutes=?,
            exam_type=?, is_active=?, deadline=?, notes=?, image_url=?
            WHERE id=?
        ''', [title, department, description, duration, exam_type, is_active, deadline, notes, image_url, exam_id])
        flash('Exam updated successfully!', 'success')
        return redirect(url_for('admin.exams'))

    return render_template('admin/exam_form.html', exam=exam)


@admin_bp.route('/exam/<int:exam_id>/delete', methods=['POST'])
@admin_required
def delete_exam(exam_id):
    # Delete related answers first
    execute_db('''
        DELETE FROM answers 
        WHERE result_id IN (SELECT id FROM results WHERE exam_id = ?)
    ''', [exam_id])
    
    # Delete related results
    execute_db('DELETE FROM results WHERE exam_id = ?', [exam_id])
    
    # Delete related questions (questions have ON DELETE CASCADE, but we'll be explicit)
    execute_db('DELETE FROM questions WHERE exam_id = ?', [exam_id])
    
    # Now delete the exam
    execute_db('DELETE FROM exams WHERE id = ?', [exam_id])
    flash('Exam deleted successfully.', 'success')
    return redirect(url_for('admin.exams'))


@admin_bp.route('/exam/<int:exam_id>/toggle', methods=['POST'])
@admin_required
def toggle_exam(exam_id):
    exam = query_db('SELECT is_active FROM exams WHERE id = ?', [exam_id], one=True)
    if exam:
        new_status = 0 if exam['is_active'] else 1
        execute_db('UPDATE exams SET is_active = ? WHERE id = ?', [new_status, exam_id])
        status_text = 'activated' if new_status else 'deactivated'
        flash(f'Exam {status_text}.', 'success')
    return redirect(url_for('admin.exams'))


@admin_bp.route('/exam/<int:exam_id>/questions', methods=['GET', 'POST'])
@admin_required
def manage_questions(exam_id):
    exam = query_db('SELECT * FROM exams WHERE id = ?', [exam_id], one=True)
    if not exam:
        flash('Exam not found.', 'error')
        return redirect(url_for('admin.exams'))

    if request.method == 'POST':
        question_text = request.form.get('question_text', '').strip()
        option_a = request.form.get('option_a', '').strip()
        option_b = request.form.get('option_b', '').strip()
        option_c = request.form.get('option_c', '').strip()
        option_d = request.form.get('option_d', '').strip()
        correct_option = request.form.get('correct_option', '')
        marks = int(request.form.get('marks', 1))

        if not all([question_text, option_a, option_b, option_c, option_d, correct_option]):
            flash('All fields are required.', 'error')
        else:
            execute_db('''
                INSERT INTO questions (exam_id, question_text, option_a, option_b, option_c, option_d, correct_option, marks)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', [exam_id, question_text, option_a, option_b, option_c, option_d, correct_option, marks])

            # Update total questions count
            count = query_db('SELECT COUNT(*) as c FROM questions WHERE exam_id = ?', [exam_id], one=True)['c']
            execute_db('UPDATE exams SET total_questions = ? WHERE id = ?', [count, exam_id])

            flash('Question added!', 'success')
            return redirect(url_for('admin.manage_questions', exam_id=exam_id))

    questions = query_db('SELECT * FROM questions WHERE exam_id = ? ORDER BY id', [exam_id])
    return render_template('admin/questions.html', exam=exam, questions=questions)


@admin_bp.route('/question/<int:question_id>/delete', methods=['POST'])
@admin_required
def delete_question(question_id):
    q = query_db('SELECT exam_id FROM questions WHERE id = ?', [question_id], one=True)
    if q:
        execute_db('DELETE FROM questions WHERE id = ?', [question_id])
        count = query_db('SELECT COUNT(*) as c FROM questions WHERE exam_id = ?', [q['exam_id']], one=True)['c']
        execute_db('UPDATE exams SET total_questions = ? WHERE id = ?', [count, q['exam_id']])
        flash('Question deleted.', 'success')
        return redirect(url_for('admin.manage_questions', exam_id=q['exam_id']))
    flash('Question not found.', 'error')
    return redirect(url_for('admin.exams'))


@admin_bp.route('/students')
@admin_required
def students():
    students = query_db('''
        SELECT u.*,
               (SELECT COUNT(*) FROM results WHERE user_id = u.id AND is_submitted = 1) as exams_taken,
               (SELECT COALESCE(ROUND(AVG(percentage), 1), 0) FROM results WHERE user_id = u.id AND is_submitted = 1) as avg_score
        FROM users u WHERE u.role = 'student'
        ORDER BY u.full_name
    ''')
    return render_template('admin/students.html', students=students)


@admin_bp.route('/reports')
@admin_required
def reports():
    exam_reports = query_db('''
        SELECT e.id, e.title, e.department,
               COUNT(r.id) as attempts,
               COALESCE(ROUND(AVG(r.percentage), 1), 0) as avg_score,
               COALESCE(MAX(r.percentage), 0) as max_score,
               COALESCE(MIN(r.percentage), 0) as min_score,
               SUM(CASE WHEN r.percentage >= 40 THEN 1 ELSE 0 END) as passed,
               SUM(CASE WHEN r.percentage < 40 THEN 1 ELSE 0 END) as failed
        FROM exams e
        LEFT JOIN results r ON e.id = r.exam_id AND r.is_submitted = 1
        GROUP BY e.id
        ORDER BY e.title
    ''')
    return render_template('admin/reports.html', reports=exam_reports)


@admin_bp.route('/student/<int:student_id>/performance')
@admin_required
def student_performance(student_id):
    """Detailed per-student performance analysis."""
    student = query_db('SELECT * FROM users WHERE id = ? AND role = "student"', [student_id], one=True)
    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('admin.students'))

    # Course-wise stats
    course_stats = query_db('''
        SELECT e.department,
               COUNT(r.id) as exams_taken,
               COALESCE(ROUND(AVG(r.percentage), 1), 0) as avg_score,
               COALESCE(MAX(r.percentage), 0) as best_score,
               COALESCE(MIN(r.percentage), 0) as worst_score
        FROM results r
        JOIN exams e ON r.exam_id = e.id
        WHERE r.user_id = ? AND r.is_submitted = 1
        GROUP BY e.department
    ''', [student_id])

    # All results
    all_results = query_db('''
        SELECT r.*, e.title as exam_title, e.department
        FROM results r
        JOIN exams e ON r.exam_id = e.id
        WHERE r.user_id = ? AND r.is_submitted = 1
        ORDER BY r.submitted_at DESC
    ''', [student_id])

    # Overall stats
    overall = query_db('''
        SELECT COUNT(r.id) as total_exams,
               COALESCE(ROUND(AVG(r.percentage), 1), 0) as avg_score,
               COALESCE(MAX(r.percentage), 0) as best_score
        FROM results r
        WHERE r.user_id = ? AND r.is_submitted = 1
    ''', [student_id], one=True)

    return render_template('admin/student_performance.html',
                           student=student, course_stats=course_stats,
                           all_results=all_results, overall=overall)


@admin_bp.route('/study-materials')
@admin_required
def study_materials():
    materials = query_db('''
        SELECT sm.*, u.full_name as author_name
        FROM study_materials sm
        LEFT JOIN users u ON sm.created_by = u.id
        ORDER BY sm.created_at DESC
    ''')
    return render_template('admin/study_materials.html', materials=materials)


@admin_bp.route('/study-materials/add', methods=['GET', 'POST'])
@admin_required
def add_material():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        course = request.form.get('course', '').strip()
        description = request.form.get('description', '').strip()
        content = request.form.get('content', '').strip()
        material_type = request.form.get('material_type', 'document')
        file_url = request.form.get('file_url', '').strip()

        # Handle file upload
        if 'file_upload' in request.files:
            file = request.files['file_upload']
            if file and file.filename:
                # Check file size (10MB max)
                file.seek(0, 2)  # Seek to end
                file_size = file.tell()
                file.seek(0)  # Reset to beginning
                
                if file_size > 10 * 1024 * 1024:
                    flash('File size must be less than 10MB.', 'error')
                    return render_template('admin/material_form.html', material=None)
                
                # Create uploads directory if not exists
                import os
                upload_dir = os.path.join('static', 'uploads', 'materials')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Generate unique filename
                import uuid
                ext = os.path.splitext(file.filename)[1]
                unique_filename = f"{uuid.uuid4().hex}{ext}"
                file_path = os.path.join(upload_dir, unique_filename)
                file.save(file_path)
                file_url = f"/static/uploads/materials/{unique_filename}"

        if not title or not course:
            flash('Title and course are required.', 'error')
        else:
            execute_db('''
                INSERT INTO study_materials (title, course, description, content, material_type, file_url, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', [title, course, description, content, material_type, file_url, current_user.id])
            flash('Study material added successfully!', 'success')
            return redirect(url_for('admin.study_materials'))

    return render_template('admin/material_form.html', material=None)


@admin_bp.route('/study-materials/<int:material_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_material(material_id):
    material = query_db('SELECT * FROM study_materials WHERE id = ?', [material_id], one=True)
    if not material:
        flash('Material not found.', 'error')
        return redirect(url_for('admin.study_materials'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        course = request.form.get('course', '').strip()
        description = request.form.get('description', '').strip()
        content = request.form.get('content', '').strip()
        material_type = request.form.get('material_type', 'document')
        file_url = request.form.get('file_url', '').strip()

        # Handle file upload
        if 'file_upload' in request.files:
            file = request.files['file_upload']
            if file and file.filename:
                # Check file size (10MB max)
                file.seek(0, 2)  # Seek to end
                file_size = file.tell()
                file.seek(0)  # Reset to beginning
                
                if file_size > 10 * 1024 * 1024:
                    flash('File size must be less than 10MB.', 'error')
                    return render_template('admin/material_form.html', material=material)
                
                # Create uploads directory if not exists
                import os
                upload_dir = os.path.join('static', 'uploads', 'materials')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Generate unique filename
                import uuid
                ext = os.path.splitext(file.filename)[1]
                unique_filename = f"{uuid.uuid4().hex}{ext}"
                file_path = os.path.join(upload_dir, unique_filename)
                file.save(file_path)
                file_url = f"/static/uploads/materials/{unique_filename}"

        execute_db('''
            UPDATE study_materials SET title=?, course=?, description=?, content=?, material_type=?, file_url=?
            WHERE id=?
        ''', [title, course, description, content, material_type, file_url, material_id])
        flash('Material updated.', 'success')
        return redirect(url_for('admin.study_materials'))

    return render_template('admin/material_form.html', material=material)


@admin_bp.route('/study-materials/<int:material_id>/delete', methods=['POST'])
@admin_required
def delete_material(material_id):
    execute_db('DELETE FROM study_materials WHERE id = ?', [material_id])
    flash('Study material deleted.', 'success')
    return redirect(url_for('admin.study_materials'))


# API endpoint to generate shareable application link
@admin_bp.route('/api/generate-share-link', methods=['GET', 'POST'])
@admin_required
def generate_share_link():
    """Generate a secure shareable link for the application."""
    import secrets
    import time
    import traceback
    from flask import request

    try:
        # Step 1: Generate cryptographically secure token
        token = secrets.token_urlsafe(32)

        # Step 2: Ensure token uniqueness (collision handling)
        max_attempts = 10
        for attempt in range(max_attempts):
            existing = query_db('SELECT id FROM share_links WHERE token = ?', [token], one=True)
            if not existing:
                break
            token = secrets.token_urlsafe(32)
            print(f'[SHARE LINK] Token collision, regenerating (attempt {attempt + 1})')

        # Step 3: Calculate expiration (30 days)
        expires_at = int(time.time()) + (30 * 24 * 60 * 60)

        # Step 4: Insert into database
        execute_db(
            'INSERT INTO share_links (token, created_by, expires_at, is_active) VALUES (?, ?, ?, ?)',
            [token, current_user.id, expires_at, 1]
        )

        # Step 5: Verify insertion
        verify_link = query_db(
            'SELECT * FROM share_links WHERE token = ?',
            [token], one=True
        )

        if not verify_link:
            print('[SHARE LINK] ERROR: Failed to verify link after insertion')
            return jsonify({
                'success': False,
                'error': 'Database error: Link not saved'
            }), 500

        # Step 6: Build share URL
        # Use environment variable or request host
        import os
        from flask import request
        public_url = os.environ.get('PUBLIC_URL', request.host_url.rstrip('/'))
        share_url = f"{public_url}/join/{token}"

        print(f'[SHARE LINK] Generated successfully: token={token[:20]}..., url={share_url}')

        return jsonify({
            'success': True,
            'share_url': share_url,
            'token': token,
            'expires_in_days': 30,
            'created_at': int(time.time())
        })

    except Exception as e:
        print(f'[SHARE LINK] ERROR: {str(e)}')
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


