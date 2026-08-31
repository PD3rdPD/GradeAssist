GradeAssist Beta — Windows Build Instructions

Files:
  GradeAssist_Teacher_Beta.py
  build_gradeassist_beta.bat
  GradeAssist_Beta_Feedback.txt

To create the standalone Windows app:
  1. Put GradeAssist_Teacher_Beta.py and build_gradeassist_beta.bat
     in the same folder on your Windows computer.
  2. Double-click build_gradeassist_beta.bat.
  3. The first build can take a few minutes.
  4. When finished, open the new "dist" folder.
  5. Give testers "GradeAssist Beta.exe".

The tester does NOT need Python, VS Code, or PyInstaller.
Only the computer doing the build needs Python.

Note:
  Windows SmartScreen may warn about an unsigned app from an unknown
  publisher. Code signing can be added later for a public release.
