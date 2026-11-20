<?php
// Admissions enquiry handler. Set $to to the admissions inbox before going live.
header('Content-Type: application/json');
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo json_encode(['ok' => false]); exit; }

$to = 'admissions@example.com'; // TODO: replace with the real admissions address
$campuses = ['jamkhandi', 'hulyal', 'bagalkot', 'vijayapura'];
$clean = function ($k, $max = 200) { return trim(mb_substr(strip_tags($_POST[$k] ?? ''), 0, $max)); };

$data = [
  'Student'   => $clean('student_name'),
  'Parent'    => $clean('parent_name'),
  'Phone'     => preg_replace('/\D/', '', $_POST['phone'] ?? ''),
  'Email'     => filter_var($_POST['email'] ?? '', FILTER_VALIDATE_EMAIL) ?: '',
  'Campus'    => in_array($_POST['campus'] ?? '', $campuses, true) ? $_POST['campus'] : '',
  'Programme' => $clean('programme', 60),
  'Hostel'    => !empty($_POST['hostel']) ? 'Yes' : 'No',
  'Message'   => $clean('message', 2000),
];
$errors = [];
if (mb_strlen($data['Student']) < 2) $errors[] = 'student_name';
if (mb_strlen($data['Parent']) < 2) $errors[] = 'parent_name';
if (!preg_match('/^[6-9]\d{9}$/', $data['Phone'])) $errors[] = 'phone';
if (!$data['Campus']) $errors[] = 'campus';
if (!$data['Programme']) $errors[] = 'programme';
if (empty($_POST['consent'])) $errors[] = 'consent';
if ($errors) { http_response_code(422); echo json_encode(['ok' => false, 'errors' => $errors]); exit; }

$body = '';
foreach ($data as $k => $v) $body .= "$k: $v\n";
$sent = mail($to, 'New admissions enquiry: ' . ucfirst($data['Campus']), $body, 'Content-Type: text/plain; charset=UTF-8');
http_response_code($sent ? 200 : 500);
echo json_encode(['ok' => $sent]);
