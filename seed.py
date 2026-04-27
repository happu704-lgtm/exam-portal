"""Seed the database with sample data for demonstration."""
from werkzeug.security import generate_password_hash
from database import init_db, execute_db, query_db


def seed():
    init_db()

    # Check if already seeded
    existing = query_db('SELECT COUNT(*) as c FROM users', one=True)
    if existing['c'] > 0:
        print("Database already has data. Skipping seed.")
        return

    print("Seeding database...")

    # Create admin
    execute_db(
        'INSERT INTO users (username, password_hash, full_name, role, email) VALUES (?, ?, ?, ?, ?)',
        ['tulasi', generate_password_hash('tulasi@2005'), 'Tulsi', 'admin', 'admin@digitalquiz.com']
    )

    # Create students
    students = [
        ('julianne', 'pass123', 'Julianne Deidre', 'STU88291', 'julianne@sanctuary.edu'),
        ('marcus', 'pass123', 'Marcus Chen', 'STU72415', 'marcus@sanctuary.edu'),
        ('priya', 'pass123', 'Priya Sharma', 'STU63842', 'priya@sanctuary.edu'),
        ('alex', 'pass123', 'Alex Thompson', 'STU91537', 'alex@sanctuary.edu'),
        ('sofia', 'pass123', 'Sofia Rodriguez', 'STU45128', 'sofia@sanctuary.edu'),
    ]
    for uname, pwd, name, sid, email in students:
        execute_db(
            'INSERT INTO users (username, password_hash, full_name, role, student_id, email) VALUES (?, ?, ?, ?, ?, ?)',
            [uname, generate_password_hash(pwd), name, 'student', sid, email]
        )

    # Create exams
    exams = [
        ('Advanced Theoretical Physics', 'SCIENCE DEPARTMENT', 'Comprehensive exam covering quantum mechanics, relativity, and thermodynamics.', 180, 'MCQ', 'Timer starts upon entry', '/static/images/physics.jpg'),
        ('Constitutional Law', 'LEGAL STUDIES', 'An essay-based examination on constitutional principles and landmark cases.', 120, 'MCQ', 'Deadline: 4:00 PM Today', '/static/images/law.jpg'),
        ('Advanced Neuroanatomy', 'MEDICINE', 'Identification and analysis of neural structures and pathways.', 90, 'MCQ', 'External monitor required', '/static/images/medicine.jpg'),
        ('Data Structures & Algorithms', 'COMPUTER SCIENCE', 'Covers arrays, trees, graphs, sorting algorithms, and complexity analysis.', 60, 'MCQ', '', '/static/images/cs.jpg'),
        ('Organic Chemistry', 'SCIENCE DEPARTMENT', 'Reactions, mechanisms, and synthesis of organic compounds.', 90, 'MCQ', '', '/static/images/chemistry.jpg'),
    ]

    for title, dept, desc, dur, etype, notes, img in exams:
        execute_db(
            'INSERT INTO exams (title, department, description, duration_minutes, exam_type, notes, image_url, created_by, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, 1, 1)',
            [title, dept, desc, dur, etype, notes, img]
        )

    # Physics questions (Exam 1)
    physics_qs = [
        ("What is the SI unit of force?", "Newton", "Joule", "Watt", "Pascal", "A", 2),
        ("Which principle states that no two electrons can have the same set of quantum numbers?", "Heisenberg Uncertainty", "Pauli Exclusion", "Aufbau Principle", "Hund's Rule", "B", 2),
        ("What is the speed of light in vacuum?", "3 × 10⁶ m/s", "3 × 10⁸ m/s", "3 × 10¹⁰ m/s", "3 × 10⁴ m/s", "B", 2),
        ("E = mc² is the equation of?", "Kinetic energy", "Potential energy", "Mass-energy equivalence", "Gravitational energy", "C", 2),
        ("Which particle has no electric charge?", "Proton", "Electron", "Neutron", "Positron", "C", 2),
        ("What is the unit of electrical resistance?", "Ampere", "Volt", "Ohm", "Watt", "C", 2),
        ("The Doppler effect is related to?", "Light intensity", "Change in frequency", "Color absorption", "Magnetic field", "B", 2),
        ("What is the first law of thermodynamics?", "Energy cannot be created or destroyed", "Entropy always increases", "Absolute zero is unattainable", "PV = nRT", "A", 2),
        ("Which force keeps planets in orbit?", "Electromagnetic", "Nuclear", "Gravitational", "Friction", "C", 2),
        ("What is Planck's constant approximately?", "6.626 × 10⁻³⁴ J·s", "9.8 m/s²", "3 × 10⁸ m/s", "1.602 × 10⁻¹⁹ C", "A", 2),
    ]

    for q in physics_qs:
        execute_db(
            'INSERT INTO questions (exam_id, question_text, option_a, option_b, option_c, option_d, correct_option, marks) VALUES (1, ?, ?, ?, ?, ?, ?, ?)',
            list(q)
        )

    # Law questions (Exam 2)
    law_qs = [
        ("What is the supreme law of India?", "Indian Penal Code", "Constitution of India", "Civil Procedure Code", "Criminal Procedure Code", "B", 2),
        ("Which article of the Indian Constitution guarantees Right to Equality?", "Article 14", "Article 19", "Article 21", "Article 32", "A", 2),
        ("Who is known as the Father of the Indian Constitution?", "Mahatma Gandhi", "Jawaharlal Nehru", "Dr. B.R. Ambedkar", "Sardar Patel", "C", 2),
        ("What is a writ of Habeas Corpus?", "Right to property", "Right to be produced before court", "Right to free speech", "Right to education", "B", 2),
        ("How many Fundamental Rights are there in Indian Constitution?", "5", "6", "7", "8", "B", 2),
        ("Which part of the Constitution deals with Directive Principles?", "Part III", "Part IV", "Part V", "Part VI", "B", 2),
        ("What is the minimum age to become President of India?", "25 years", "30 years", "35 years", "40 years", "C", 2),
        ("Which amendment is known as the 'Mini Constitution'?", "42nd", "44th", "52nd", "73rd", "A", 2),
    ]

    for q in law_qs:
        execute_db(
            'INSERT INTO questions (exam_id, question_text, option_a, option_b, option_c, option_d, correct_option, marks) VALUES (2, ?, ?, ?, ?, ?, ?, ?)',
            list(q)
        )

    # Medicine questions (Exam 3)
    med_qs = [
        ("Which part of the brain controls balance?", "Cerebrum", "Cerebellum", "Medulla", "Pons", "B", 2),
        ("What is the largest organ in the human body?", "Liver", "Brain", "Skin", "Heart", "C", 2),
        ("How many pairs of cranial nerves are there?", "10", "12", "14", "8", "B", 2),
        ("Which neurotransmitter is associated with happiness?", "Dopamine", "Serotonin", "Acetylcholine", "GABA", "B", 2),
        ("The blood-brain barrier is formed by?", "Neurons", "Astrocytes", "Microglia", "Oligodendrocytes", "B", 2),
        ("Which lobe of the brain is responsible for vision?", "Frontal", "Temporal", "Parietal", "Occipital", "D", 2),
        ("What is the gap between two neurons called?", "Axon", "Dendrite", "Synapse", "Myelin", "C", 2),
        ("Which cranial nerve is the longest?", "Trigeminal", "Vagus", "Facial", "Optic", "B", 2),
    ]

    for q in med_qs:
        execute_db(
            'INSERT INTO questions (exam_id, question_text, option_a, option_b, option_c, option_d, correct_option, marks) VALUES (3, ?, ?, ?, ?, ?, ?, ?)',
            list(q)
        )

    # CS questions (Exam 4)
    cs_qs = [
        ("What is the time complexity of binary search?", "O(n)", "O(log n)", "O(n²)", "O(1)", "B", 2),
        ("Which data structure uses FIFO?", "Stack", "Queue", "Tree", "Graph", "B", 2),
        ("What is a complete binary tree?", "All leaves at same level", "Every node has 2 children", "All levels filled except possibly last", "No node has more than one child", "C", 2),
        ("Which sorting algorithm has the best average case?", "Bubble Sort", "Selection Sort", "Merge Sort", "Insertion Sort", "C", 2),
        ("What is the worst case of QuickSort?", "O(n log n)", "O(n²)", "O(n)", "O(log n)", "B", 2),
        ("A graph with no cycles is called?", "Complete graph", "Tree", "Bipartite graph", "Multigraph", "B", 2),
        ("Which data structure is used in BFS?", "Stack", "Queue", "Priority Queue", "Array", "B", 2),
        ("What is the space complexity of merge sort?", "O(1)", "O(log n)", "O(n)", "O(n²)", "C", 2),
    ]

    for q in cs_qs:
        execute_db(
            'INSERT INTO questions (exam_id, question_text, option_a, option_b, option_c, option_d, correct_option, marks) VALUES (4, ?, ?, ?, ?, ?, ?, ?)',
            list(q)
        )

    # Chemistry questions (Exam 5)
    chem_qs = [
        ("What is the functional group in alcohols?", "-CHO", "-COOH", "-OH", "-NH₂", "C", 2),
        ("Which reaction converts an alkene to an alkane?", "Oxidation", "Hydrogenation", "Dehydration", "Halogenation", "B", 2),
        ("What type of isomerism do mirror-image molecules exhibit?", "Structural", "Geometric", "Optical", "Positional", "C", 2),
        ("Benzene has how many pi electrons?", "2", "4", "6", "8", "C", 2),
        ("Which reagent is used in Grignard reaction?", "NaOH", "RMgX", "KMnO₄", "H₂SO₄", "B", 2),
        ("SN2 reaction follows which mechanism?", "First order", "Second order", "Zero order", "Third order", "B", 2),
        ("What is the IUPAC name of CH₃CHO?", "Methanol", "Ethanal", "Ethanol", "Methanal", "B", 2),
        ("Which test distinguishes aldehydes from ketones?", "Litmus test", "Tollen's test", "Flame test", "pH test", "B", 2),
    ]

    for q in chem_qs:
        execute_db(
            'INSERT INTO questions (exam_id, question_text, option_a, option_b, option_c, option_d, correct_option, marks) VALUES (5, ?, ?, ?, ?, ?, ?, ?)',
            list(q)
        )

    # Update question counts
    for i in range(1, 6):
        count = query_db('SELECT COUNT(*) as c FROM questions WHERE exam_id = ?', [i], one=True)['c']
        execute_db('UPDATE exams SET total_questions = ? WHERE id = ?', [count, i])

    # Seed study materials
    study_materials = [
        ('Quantum Mechanics Fundamentals', 'SCIENCE DEPARTMENT', 'document',
         'Core concepts of quantum mechanics for beginners.',
         'Quantum mechanics is the branch of physics that deals with the behavior of matter and energy at the smallest scales.\n\nKey Concepts:\n1. Wave-Particle Duality: Particles like electrons exhibit both wave-like and particle-like properties.\n2. Heisenberg Uncertainty Principle: You cannot simultaneously know the exact position and momentum of a particle.\n3. Schrödinger Equation: The fundamental equation of quantum mechanics that describes how the quantum state of a system changes over time.\n4. Superposition: A quantum system can exist in multiple states simultaneously until measured.\n5. Quantum Entanglement: Two particles can be connected such that measuring one instantly affects the other.\n\nImportant Formulas:\n- E = hf (Energy of a photon)\n- λ = h/p (de Broglie wavelength)\n- ΔxΔp ≥ ℏ/2 (Uncertainty principle)'),

        ('Thermodynamics Laws Summary', 'SCIENCE DEPARTMENT', 'notes',
         'Quick reference notes on the four laws of thermodynamics.',
         'THE FOUR LAWS OF THERMODYNAMICS\n\nZeroth Law: If system A is in thermal equilibrium with system C, and system B is also in thermal equilibrium with system C, then A and B are in thermal equilibrium with each other.\n\nFirst Law (Conservation of Energy): Energy cannot be created or destroyed, only transformed. ΔU = Q - W\n\nSecond Law (Entropy): The total entropy of an isolated system always increases over time. Heat flows naturally from hot to cold objects.\n\nThird Law: As temperature approaches absolute zero, the entropy of a perfect crystal approaches zero.'),

        ('Indian Constitution Overview', 'LEGAL STUDIES', 'document',
         'Comprehensive study guide on the Indian Constitution and its key features.',
         'THE CONSTITUTION OF INDIA\n\nThe Constitution of India is the longest written constitution in the world. It was adopted on 26 November 1949 and came into effect on 26 January 1950.\n\nKey Features:\n1. Preamble - "We, the people of India" - declares India as a Sovereign, Socialist, Secular, Democratic Republic\n2. Fundamental Rights (Part III, Articles 12-35) - Right to Equality, Freedom, Against Exploitation, Freedom of Religion, Cultural and Educational Rights, Constitutional Remedies\n3. Directive Principles (Part IV) - Guidelines for the state to establish a just society\n4. Fundamental Duties (Part IVA, Article 51A) - 11 duties of every citizen\n5. Federal Structure with Unitary Bias - Division of powers between Centre and States\n\nImportant Articles:\n- Article 14: Right to Equality\n- Article 19: Freedom of Speech\n- Article 21: Right to Life\n- Article 32: Right to Constitutional Remedies\n- Article 370: Special Status of J&K (now abrogated)'),

        ('Landmark Supreme Court Cases', 'LEGAL STUDIES', 'notes',
         'Important landmark cases every law student must know.',
         'LANDMARK CASES:\n\n1. Kesavananda Bharati v. State of Kerala (1973) - Basic Structure Doctrine\n2. Maneka Gandhi v. Union of India (1978) - Expanded scope of Article 21\n3. Vishaka v. State of Rajasthan (1997) - Sexual harassment at workplace\n4. Navtej Singh Johar v. Union of India (2018) - Decriminalized Section 377\n5. K.S. Puttaswamy v. Union of India (2017) - Right to Privacy as fundamental right'),

        ('Neuroanatomy: Brain Regions', 'MEDICINE', 'document',
         'Detailed guide to brain regions and their functions.',
         'MAJOR BRAIN REGIONS AND FUNCTIONS\n\n1. CEREBRUM (largest part)\n   - Frontal Lobe: Decision making, personality, motor function\n   - Parietal Lobe: Sensory processing, spatial awareness\n   - Temporal Lobe: Hearing, memory, language comprehension\n   - Occipital Lobe: Visual processing\n\n2. CEREBELLUM\n   - Balance and coordination\n   - Fine motor control\n   - Motor learning\n\n3. BRAINSTEM\n   - Midbrain: Eye movement, auditory/visual processing\n   - Pons: Sleep, respiration, swallowing\n   - Medulla Oblongata: Heart rate, breathing, blood pressure\n\n4. LIMBIC SYSTEM\n   - Hippocampus: Memory formation\n   - Amygdala: Emotional processing, fear response\n   - Hypothalamus: Homeostasis, hormone regulation'),

        ('Cranial Nerves Quick Reference', 'MEDICINE', 'notes',
         'Mnemonic and summary of all 12 cranial nerves.',
         '12 CRANIAL NERVES\n\nMnemonic: "Oh, Oh, Oh, To Touch And Feel Very Good Velvet, AH!"\n\nI. Olfactory - Smell (Sensory)\nII. Optic - Vision (Sensory)\nIII. Oculomotor - Eye movement (Motor)\nIV. Trochlear - Eye movement (Motor)\nV. Trigeminal - Face sensation, chewing (Both)\nVI. Abducens - Eye movement (Motor)\nVII. Facial - Facial expression, taste (Both)\nVIII. Vestibulocochlear - Hearing, balance (Sensory)\nIX. Glossopharyngeal - Taste, swallowing (Both)\nX. Vagus - Organs, digestion (Both) - LONGEST cranial nerve\nXI. Accessory - Head/shoulder movement (Motor)\nXII. Hypoglossal - Tongue movement (Motor)'),

        ('Data Structures Cheat Sheet', 'COMPUTER SCIENCE', 'document',
         'Time complexity reference for common data structures.',
         'DATA STRUCTURES TIME COMPLEXITY\n\n| Structure     | Access | Search | Insert | Delete |\n|--------------|--------|--------|--------|--------|\n| Array        | O(1)   | O(n)   | O(n)   | O(n)   |\n| Linked List  | O(n)   | O(n)   | O(1)   | O(1)   |\n| Stack        | O(n)   | O(n)   | O(1)   | O(1)   |\n| Queue        | O(n)   | O(n)   | O(1)   | O(1)   |\n| Hash Table   | N/A    | O(1)   | O(1)   | O(1)   |\n| BST          | O(logn)| O(logn)| O(logn)| O(logn)|\n| Heap         | N/A    | O(n)   | O(logn)| O(logn)|\n\nKey Concepts:\n- Stack: LIFO (Last In, First Out) - used for function calls, undo operations\n- Queue: FIFO (First In, First Out) - used for BFS, scheduling\n- Binary Search Tree: Left < Root < Right\n- Heap: Min-heap (parent ≤ children) or Max-heap (parent ≥ children)'),

        ('Sorting Algorithms Guide', 'COMPUTER SCIENCE', 'notes',
         'Comparison of popular sorting algorithms with use cases.',
         'SORTING ALGORITHMS COMPARISON\n\n1. Bubble Sort - O(n²) avg, O(1) space - Simple but slow\n2. Selection Sort - O(n²) avg, O(1) space - Fewer swaps than bubble\n3. Insertion Sort - O(n²) avg, O(1) space - Good for nearly sorted data\n4. Merge Sort - O(n log n) avg, O(n) space - Stable, divide & conquer\n5. Quick Sort - O(n log n) avg, O(log n) space - Fastest in practice\n6. Heap Sort - O(n log n) avg, O(1) space - In-place, not stable\n\nBest for small arrays: Insertion Sort\nBest overall: Quick Sort (avg case)\nBest guaranteed: Merge Sort (always O(n log n))\nBest for space: Heap Sort (O(1) extra space)'),

        ('Organic Reaction Mechanisms', 'SCIENCE DEPARTMENT', 'document',
         'Study guide for organic chemistry reaction mechanisms.',
         'ORGANIC REACTION MECHANISMS\n\n1. SN1 (Substitution Nucleophilic Unimolecular)\n   - Two steps: carbocation formation, then nucleophilic attack\n   - Favored by tertiary substrates, polar protic solvents\n   - Rate = k[substrate]\n\n2. SN2 (Substitution Nucleophilic Bimolecular)\n   - One step: backside attack with inversion\n   - Favored by primary substrates, strong nucleophiles\n   - Rate = k[substrate][nucleophile]\n\n3. E1 (Elimination Unimolecular)\n   - Two steps: carbocation formation, then proton removal\n   - Competes with SN1\n\n4. E2 (Elimination Bimolecular)\n   - One step: anti-periplanar elimination\n   - Requires strong base\n   - Rate = k[substrate][base]'),

        ('Grignard Reagent Applications', 'SCIENCE DEPARTMENT', 'notes',
         'How to use Grignard reagents in organic synthesis.',
         'GRIGNARD REAGENTS (RMgX)\n\nFormation: R-X + Mg → RMgX (in dry ether)\n\nReactions:\n1. With Aldehydes → Secondary Alcohols\n2. With Ketones → Tertiary Alcohols\n3. With Formaldehyde → Primary Alcohols\n4. With CO₂ → Carboxylic Acids\n5. With Esters → Tertiary Alcohols\n6. With Epoxides → Extends carbon chain by 2\n\nIMPORTANT: Grignard reagents are:\n- Strong nucleophiles\n- Strong bases\n- React with water, alcohols, acids (avoid protic solvents!)\n- Must use anhydrous conditions'),
    ]

    admin_id = query_db('SELECT id FROM users WHERE role = "admin"', one=True)['id']
    for title, course, mtype, desc, content in study_materials:
        execute_db(
            'INSERT INTO study_materials (title, course, description, content, material_type, created_by) VALUES (?, ?, ?, ?, ?, ?)',
            [title, course, desc, content, mtype, admin_id]
        )

    print("✅ Database seeded successfully!")
    print("\n📋 Login Credentials:")
    print("  Admin:   username='admin'    password='admin123'")
    print("  Student: username='julianne' password='pass123'")
    print("  Student: username='marcus'   password='pass123'")
    print("  Student: username='priya'    password='pass123'")


if __name__ == '__main__':
    seed()
