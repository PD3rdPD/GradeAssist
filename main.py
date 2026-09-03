"""Polished multilingual Android Student Grade Calculator."""

from __future__ import annotations

import json
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.utils import platform

from calculator_logic import (
    calculate_average,
    calculate_required_grade,
    calculate_weighted_average,
    generate_grade_paths,
    letter_grade,
    parse_grades,
)

APP_NAME = "Grade Assist"
APP_VERSION = "1.0.0"
TAGLINE = "Plan. Calculate. Improve."

# =========================================================
# LANGUAGES
# =========================================================

LANGUAGES = {
    "English": {
        "title": "Grade Assist",
        "subtitle": "Plan. Calculate. Improve.",
        "language": "Language",

        "student_section": "Student Information",
        "student_name": "Student Name",
        "grades": "Grades",
        "grades_hint": "Example: 85, 92, 78, 100",

        "allow_over_100": "Allow grades over 100",
        "use_extra_credit": "Use standalone extra credit",
        "extra_credit": "Standalone Extra Credit Points",

        "calculate": "Calculate Grade",

        "current_results": "Current Grade",
        "average": "Average",
        "letter_grade": "Letter Grade",

        "goal_section": "Grade Goal",
        "desired_grade": "Desired Final Grade",
        "target_hint": "Example: 90",
        "remaining": "Remaining Assignments",
        "remaining_hint": "Example: 5",
        "goal": "Calculate Grade Goal",

        "path": "Grade Path Planning",
        "path_results": "Grade Path Results",
        "path_placeholder": (
            "Your personalized grade paths will appear here."
        ),

        "clear": "Clear / Reset",

        "missing_name": "Please enter the student's name.",
        "missing_grades": "Please enter at least one grade.",
        "blank_grade": "Grades cannot contain blank entries.",
        "invalid_grade": "'{value}' is not a valid number.",
        "negative_grade": "Grades cannot be negative.",
        "over_100_error": (
            "Turn on 'Allow grades over 100' before entering "
            "a grade above 100."
        ),

        "invalid_extra_credit": (
            "Extra credit points must be a valid number."
        ),
        "extra_credit_negative": (
            "Extra credit cannot be negative."
        ),

        "calculate_first": (
            "Please calculate the current grade first."
        ),

        "enter_target": "Please enter a desired final grade.",
        "invalid_target": (
            "Desired final grade must be a number between 0 and 100."
        ),

        "enter_remaining": (
            "Please enter the number of remaining assignments."
        ),
        "invalid_remaining": (
            "Remaining assignments must be a whole number "
            "greater than zero."
        ),

        "goal_secured": (
            "You have already secured your target average."
        ),

        "not_achievable": (
            "This target is not achievable with grades capped at 100%."
        ),

        "extra_credit_possible": (
            "This may be possible if grades above 100 are available."
        ),

        "need_average": (
            "You need an average of {needed:.2f}% on the "
            "remaining {remaining} assignment(s)."
        ),

        "need_over_100": (
            "You would need an average of {needed:.2f}%."
        ),

        "no_path": (
            "No achievable grade path could be generated "
            "for these values."
        ),

        "target_average": "Target Average",
        "average_needed": "Average Needed",

        "consistent": "Consistent Path",
        "strong_finish": "Strong Finish",
        "strong_start": "Strong Start",
        "buffer": "Buffer Path",
        "assignment": "Assignment",

        "feedback_a": (
            "Excellent work! You are currently performing at an A level."
        ),
        "feedback_b": (
            "You are doing well. A few stronger grades could "
            "move you toward an A."
        ),
        "feedback_c": (
            "You are passing, but stronger upcoming grades "
            "could significantly improve your average."
        ),
        "feedback_d": (
            "Your grade is currently at risk. Focus on upcoming "
            "assignments and available extra credit."
        ),
        "feedback_f": (
            "Your current average is below passing. Focus on "
            "upcoming assignments and recovery opportunities."
        ),

        "below_target": (
            "You are {difference:.2f} percentage points "
            "below your {target:.2f}% target."
        ),
        "above_target": (
            "You are {difference:.2f} percentage points "
            "above your target."
        ),
        "at_target": "You are exactly at your target.",
    },

    "Español": {
        "title": "Grade Assist",
        "subtitle": "Planifica. Calcula. Mejora.",
        "language": "Idioma",

        "student_section": "Información del Estudiante",
        "student_name": "Nombre del Estudiante",
        "grades": "Calificaciones",
        "grades_hint": "Ejemplo: 85, 92, 78, 100",

        "allow_over_100": "Permitir calificaciones mayores de 100",
        "use_extra_credit": "Usar crédito extra independiente",
        "extra_credit": "Puntos de Crédito Extra",

        "calculate": "Calcular Calificación",

        "current_results": "Calificación Actual",
        "average": "Promedio",
        "letter_grade": "Letra",

        "goal_section": "Meta de Calificación",
        "desired_grade": "Calificación Final Deseada",
        "target_hint": "Ejemplo: 90",
        "remaining": "Tareas Restantes",
        "remaining_hint": "Ejemplo: 5",
        "goal": "Calcular Meta",

        "path": "Plan de Calificaciones",
        "path_results": "Resultados del Plan",
        "path_placeholder": (
            "Tus planes personalizados aparecerán aquí."
        ),

        "clear": "Borrar / Reiniciar",

        "missing_name": "Ingrese el nombre del estudiante.",
        "missing_grades": "Ingrese al menos una calificación.",
        "blank_grade": (
            "Las calificaciones no pueden contener espacios vacíos."
        ),
        "invalid_grade": "'{value}' no es un número válido.",
        "negative_grade": "Las calificaciones no pueden ser negativas.",
        "over_100_error": (
            "Active 'Permitir calificaciones mayores de 100' "
            "antes de ingresar una calificación superior a 100."
        ),

        "invalid_extra_credit": (
            "Los puntos de crédito extra deben ser un número válido."
        ),
        "extra_credit_negative": (
            "El crédito extra no puede ser negativo."
        ),

        "calculate_first": (
            "Primero calcule la calificación actual."
        ),

        "enter_target": (
            "Ingrese la calificación final deseada."
        ),
        "invalid_target": (
            "La calificación final deseada debe ser un número "
            "entre 0 y 100."
        ),

        "enter_remaining": (
            "Ingrese el número de tareas restantes."
        ),
        "invalid_remaining": (
            "Las tareas restantes deben ser un número entero "
            "mayor que cero."
        ),

        "goal_secured": (
            "Ya ha asegurado su promedio objetivo."
        ),

        "not_achievable": (
            "Esta meta no se puede alcanzar con "
            "calificaciones limitadas a 100%."
        ),

        "extra_credit_possible": (
            "Puede ser posible si hay calificaciones "
            "superiores a 100 disponibles."
        ),

        "need_average": (
            "Necesita un promedio de {needed:.2f}% en las "
            "{remaining} tarea(s) restantes."
        ),

        "need_over_100": (
            "Necesitaría un promedio de {needed:.2f}%."
        ),

        "no_path": (
            "No se pudo generar un plan alcanzable "
            "para estos valores."
        ),

        "target_average": "Promedio Objetivo",
        "average_needed": "Promedio Necesario",

        "consistent": "Plan Constante",
        "strong_finish": "Final Fuerte",
        "strong_start": "Inicio Fuerte",
        "buffer": "Plan con Margen",
        "assignment": "Tarea",

        "feedback_a": (
            "¡Excelente trabajo! Actualmente tiene un nivel de A."
        ),
        "feedback_b": (
            "Va bien. Algunas calificaciones más altas podrían "
            "acercarlo a una A."
        ),
        "feedback_c": (
            "Está aprobando, pero mejores calificaciones futuras "
            "podrían aumentar considerablemente su promedio."
        ),
        "feedback_d": (
            "Su calificación está en riesgo. Concéntrese en las "
            "próximas tareas y el crédito extra disponible."
        ),
        "feedback_f": (
            "Su promedio actual está por debajo de aprobación. "
            "Concéntrese en las próximas tareas y oportunidades "
            "de recuperación."
        ),

        "below_target": (
            "Está {difference:.2f} puntos porcentuales por debajo "
            "de su meta de {target:.2f}%."
        ),
        "above_target": (
            "Está {difference:.2f} puntos porcentuales "
            "por encima de su meta."
        ),
        "at_target": "Está exactamente en su meta.",
    },

    "Français": {
        "title": "Grade Assist",
        "subtitle": "Planifiez. Calculez. Progressez.",
        "language": "Langue",

        "student_section": "Informations de l'Étudiant",
        "student_name": "Nom de l'Étudiant",
        "grades": "Notes",
        "grades_hint": "Exemple : 85, 92, 78, 100",

        "allow_over_100": "Autoriser les notes supérieures à 100",
        "use_extra_credit": "Utiliser des points bonus séparés",
        "extra_credit": "Points de Bonus",

        "calculate": "Calculer la Note",

        "current_results": "Note Actuelle",
        "average": "Moyenne",
        "letter_grade": "Note Lettre",

        "goal_section": "Objectif de Note",
        "desired_grade": "Moyenne Finale Souhaitée",
        "target_hint": "Exemple : 90",
        "remaining": "Travaux Restants",
        "remaining_hint": "Exemple : 5",
        "goal": "Calculer l'Objectif",

        "path": "Planification des Notes",
        "path_results": "Résultats du Plan",
        "path_placeholder": (
            "Vos plans personnalisés apparaîtront ici."
        ),

        "clear": "Effacer / Réinitialiser",

        "missing_name": "Veuillez entrer le nom de l'étudiant.",
        "missing_grades": "Veuillez entrer au moins une note.",
        "blank_grade": "Les notes ne peuvent pas contenir de valeur vide.",
        "invalid_grade": "'{value}' n'est pas un nombre valide.",
        "negative_grade": "Les notes ne peuvent pas être négatives.",
        "over_100_error": (
            "Activez l'option permettant les notes supérieures "
            "à 100 avant d'en entrer une."
        ),

        "invalid_extra_credit": (
            "Les points bonus doivent être un nombre valide."
        ),
        "extra_credit_negative": (
            "Les points bonus ne peuvent pas être négatifs."
        ),

        "calculate_first": (
            "Calculez d'abord la note actuelle."
        ),

        "enter_target": (
            "Veuillez entrer la moyenne finale souhaitée."
        ),
        "invalid_target": (
            "La moyenne finale souhaitée doit être un nombre "
            "entre 0 et 100."
        ),

        "enter_remaining": (
            "Veuillez entrer le nombre de travaux restants."
        ),
        "invalid_remaining": (
            "Le nombre de travaux restants doit être un entier "
            "supérieur à zéro."
        ),

        "goal_secured": (
            "Vous avez déjà atteint votre moyenne cible."
        ),

        "not_achievable": (
            "Cet objectif n'est pas réalisable avec des notes "
            "limitées à 100%."
        ),

        "extra_credit_possible": (
            "Cela peut être possible si des notes supérieures "
            "à 100 sont disponibles."
        ),

        "need_average": (
            "Vous avez besoin d'une moyenne de {needed:.2f}% "
            "sur les {remaining} travaux restants."
        ),

        "need_over_100": (
            "Vous auriez besoin d'une moyenne de {needed:.2f}%."
        ),

        "no_path": (
            "Aucun plan réalisable n'a pu être généré "
            "pour ces valeurs."
        ),

        "target_average": "Moyenne Cible",
        "average_needed": "Moyenne Nécessaire",

        "consistent": "Plan Régulier",
        "strong_finish": "Fin Forte",
        "strong_start": "Début Fort",
        "buffer": "Plan avec Marge",
        "assignment": "Travail",

        "feedback_a": (
            "Excellent travail ! Vous êtes actuellement au niveau A."
        ),
        "feedback_b": (
            "Vous vous en sortez bien. Quelques meilleures notes "
            "pourraient vous rapprocher d'un A."
        ),
        "feedback_c": (
            "Vous réussissez, mais de meilleures notes à venir "
            "pourraient améliorer votre moyenne."
        ),
        "feedback_d": (
            "Votre note est actuellement à risque. Concentrez-vous "
            "sur les prochains travaux et les bonus disponibles."
        ),
        "feedback_f": (
            "Votre moyenne actuelle est insuffisante. Concentrez-vous "
            "sur les prochains travaux et les possibilités de rattrapage."
        ),

        "below_target": (
            "Vous êtes à {difference:.2f} points de pourcentage "
            "sous votre objectif de {target:.2f}%."
        ),
        "above_target": (
            "Vous êtes à {difference:.2f} points de pourcentage "
            "au-dessus de votre objectif."
        ),
        "at_target": "Vous êtes exactement à votre objectif.",
    },

    "Deutsch": {
        "title": "Grade Assist",
        "subtitle": "Planen. Berechnen. Verbessern.",
        "language": "Sprache",

        "student_section": "Schülerinformationen",
        "student_name": "Name des Schülers",
        "grades": "Noten",
        "grades_hint": "Beispiel: 85, 92, 78, 100",

        "allow_over_100": "Noten über 100 zulassen",
        "use_extra_credit": "Separate Bonuspunkte verwenden",
        "extra_credit": "Zusätzliche Bonuspunkte",

        "calculate": "Note Berechnen",

        "current_results": "Aktuelle Note",
        "average": "Durchschnitt",
        "letter_grade": "Buchstabennote",

        "goal_section": "Notenziel",
        "desired_grade": "Gewünschte Endnote",
        "target_hint": "Beispiel: 90",
        "remaining": "Verbleibende Aufgaben",
        "remaining_hint": "Beispiel: 5",
        "goal": "Notenziel Berechnen",

        "path": "Notenplanung",
        "path_results": "Planungsergebnisse",
        "path_placeholder": (
            "Ihre persönlichen Notenpläne erscheinen hier."
        ),

        "clear": "Löschen / Zurücksetzen",

        "missing_name": "Bitte geben Sie den Namen des Schülers ein.",
        "missing_grades": "Bitte geben Sie mindestens eine Note ein.",
        "blank_grade": "Noten dürfen keine leeren Einträge enthalten.",
        "invalid_grade": "'{value}' ist keine gültige Zahl.",
        "negative_grade": "Noten dürfen nicht negativ sein.",
        "over_100_error": (
            "Aktivieren Sie zuerst 'Noten über 100 zulassen'."
        ),

        "invalid_extra_credit": (
            "Bonuspunkte müssen eine gültige Zahl sein."
        ),
        "extra_credit_negative": (
            "Bonuspunkte dürfen nicht negativ sein."
        ),

        "calculate_first": (
            "Bitte berechnen Sie zuerst die aktuelle Note."
        ),

        "enter_target": "Bitte geben Sie die gewünschte Endnote ein.",
        "invalid_target": (
            "Die gewünschte Endnote muss zwischen 0 und 100 liegen."
        ),

        "enter_remaining": (
            "Bitte geben Sie die Anzahl der verbleibenden Aufgaben ein."
        ),
        "invalid_remaining": (
            "Verbleibende Aufgaben müssen eine ganze Zahl "
            "größer als null sein."
        ),

        "goal_secured": (
            "Sie haben Ihr Ziel bereits erreicht."
        ),

        "not_achievable": (
            "Dieses Ziel ist mit auf 100% begrenzten Noten "
            "nicht erreichbar."
        ),

        "extra_credit_possible": (
            "Dies könnte möglich sein, wenn Noten über 100 "
            "verfügbar sind."
        ),

        "need_average": (
            "Sie benötigen bei den verbleibenden {remaining} "
            "Aufgaben einen Durchschnitt von {needed:.2f}%."
        ),

        "need_over_100": (
            "Sie würden einen Durchschnitt von {needed:.2f}% benötigen."
        ),

        "no_path": (
            "Für diese Werte konnte kein erreichbarer Plan erstellt werden."
        ),

        "target_average": "Zieldurchschnitt",
        "average_needed": "Benötigter Durchschnitt",

        "consistent": "Konstanter Plan",
        "strong_finish": "Starker Abschluss",
        "strong_start": "Starker Start",
        "buffer": "Pufferplan",
        "assignment": "Aufgabe",

        "feedback_a": (
            "Ausgezeichnet! Sie befinden sich derzeit auf A-Niveau."
        ),
        "feedback_b": (
            "Sie machen gute Fortschritte. Einige stärkere Noten "
            "könnten Sie näher an ein A bringen."
        ),
        "feedback_c": (
            "Sie bestehen, aber bessere kommende Noten könnten "
            "Ihren Durchschnitt deutlich verbessern."
        ),
        "feedback_d": (
            "Ihre Note ist gefährdet. Konzentrieren Sie sich auf "
            "kommende Aufgaben und verfügbare Bonuspunkte."
        ),
        "feedback_f": (
            "Ihr aktueller Durchschnitt liegt unter dem Bestehensniveau. "
            "Konzentrieren Sie sich auf kommende Aufgaben."
        ),

        "below_target": (
            "Sie liegen {difference:.2f} Prozentpunkte unter "
            "Ihrem Ziel von {target:.2f}%."
        ),
        "above_target": (
            "Sie liegen {difference:.2f} Prozentpunkte über Ihrem Ziel."
        ),
        "at_target": "Sie liegen genau auf Ihrem Ziel.",
    },

    "Português": {
        "title": "Grade Assist",
        "subtitle": "Planeje. Calcule. Melhore.",
        "language": "Idioma",

        "student_section": "Informações do Aluno",
        "student_name": "Nome do Aluno",
        "grades": "Notas",
        "grades_hint": "Exemplo: 85, 92, 78, 100",

        "allow_over_100": "Permitir notas acima de 100",
        "use_extra_credit": "Usar pontos extras separados",
        "extra_credit": "Pontos Extras",

        "calculate": "Calcular Nota",

        "current_results": "Nota Atual",
        "average": "Média",
        "letter_grade": "Conceito",

        "goal_section": "Meta de Nota",
        "desired_grade": "Nota Final Desejada",
        "target_hint": "Exemplo: 90",
        "remaining": "Atividades Restantes",
        "remaining_hint": "Exemplo: 5",
        "goal": "Calcular Meta",

        "path": "Planejamento de Notas",
        "path_results": "Resultados do Planejamento",
        "path_placeholder": (
            "Seus planos personalizados aparecerão aqui."
        ),

        "clear": "Limpar / Reiniciar",

        "missing_name": "Digite o nome do aluno.",
        "missing_grades": "Digite pelo menos uma nota.",
        "blank_grade": "As notas não podem conter entradas vazias.",
        "invalid_grade": "'{value}' não é um número válido.",
        "negative_grade": "As notas não podem ser negativas.",
        "over_100_error": (
            "Ative 'Permitir notas acima de 100' antes de "
            "digitar uma nota superior a 100."
        ),

        "invalid_extra_credit": (
            "Os pontos extras devem ser um número válido."
        ),
        "extra_credit_negative": (
            "Os pontos extras não podem ser negativos."
        ),

        "calculate_first": (
            "Calcule primeiro a nota atual."
        ),

        "enter_target": "Digite a nota final desejada.",
        "invalid_target": (
            "A nota final desejada deve estar entre 0 e 100."
        ),

        "enter_remaining": (
            "Digite o número de atividades restantes."
        ),
        "invalid_remaining": (
            "As atividades restantes devem ser um número inteiro "
            "maior que zero."
        ),

        "goal_secured": (
            "Você já garantiu sua média desejada."
        ),

        "not_achievable": (
            "Essa meta não pode ser alcançada com notas "
            "limitadas a 100%."
        ),

        "extra_credit_possible": (
            "Isso pode ser possível se notas acima de 100 "
            "estiverem disponíveis."
        ),

        "need_average": (
            "Você precisa de uma média de {needed:.2f}% nas "
            "{remaining} atividades restantes."
        ),

        "need_over_100": (
            "Você precisaria de uma média de {needed:.2f}%."
        ),

        "no_path": (
            "Não foi possível gerar um plano alcançável "
            "para esses valores."
        ),

        "target_average": "Média Desejada",
        "average_needed": "Média Necessária",

        "consistent": "Plano Consistente",
        "strong_finish": "Final Forte",
        "strong_start": "Início Forte",
        "buffer": "Plano com Margem",
        "assignment": "Atividade",

        "feedback_a": (
            "Excelente trabalho! Você está atualmente no nível A."
        ),
        "feedback_b": (
            "Você está indo bem. Algumas notas mais altas podem "
            "aproximá-lo de um A."
        ),
        "feedback_c": (
            "Você está aprovado, mas notas melhores nas próximas "
            "atividades podem aumentar bastante sua média."
        ),
        "feedback_d": (
            "Sua nota está em risco. Concentre-se nas próximas "
            "atividades e nos pontos extras disponíveis."
        ),
        "feedback_f": (
            "Sua média atual está abaixo da aprovação. Concentre-se "
            "nas próximas atividades e oportunidades de recuperação."
        ),

        "below_target": (
            "Você está {difference:.2f} pontos percentuais abaixo "
            "da sua meta de {target:.2f}%."
        ),
        "above_target": (
            "Você está {difference:.2f} pontos percentuais "
            "acima da sua meta."
        ),
        "at_target": "Você está exatamente na sua meta.",
    },

    "中文": {
        "title": "Grade Assist",
        "subtitle": "规划。计算。提高。",
        "language": "语言",

        "student_section": "学生信息",
        "student_name": "学生姓名",
        "grades": "成绩",
        "grades_hint": "示例：85, 92, 78, 100",

        "allow_over_100": "允许超过100分的成绩",
        "use_extra_credit": "使用独立额外加分",
        "extra_credit": "额外加分",

        "calculate": "计算成绩",

        "current_results": "当前成绩",
        "average": "平均分",
        "letter_grade": "等级",

        "goal_section": "成绩目标",
        "desired_grade": "目标最终成绩",
        "target_hint": "示例：90",
        "remaining": "剩余作业数量",
        "remaining_hint": "示例：5",
        "goal": "计算目标成绩",

        "path": "成绩路径规划",
        "path_results": "成绩路径结果",
        "path_placeholder": "个性化成绩路径将在这里显示。",

        "clear": "清除 / 重置",

        "missing_name": "请输入学生姓名。",
        "missing_grades": "请至少输入一个成绩。",
        "blank_grade": "成绩中不能包含空白项目。",
        "invalid_grade": "'{value}' 不是有效数字。",
        "negative_grade": "成绩不能为负数。",
        "over_100_error": "输入超过100的成绩前，请启用相应选项。",

        "invalid_extra_credit": "额外加分必须是有效数字。",
        "extra_credit_negative": "额外加分不能为负数。",

        "calculate_first": "请先计算当前成绩。",

        "enter_target": "请输入目标最终成绩。",
        "invalid_target": "目标最终成绩必须在0到100之间。",

        "enter_remaining": "请输入剩余作业数量。",
        "invalid_remaining": "剩余作业必须是大于零的整数。",

        "goal_secured": "您已经达到目标平均分。",

        "not_achievable": "如果成绩最高为100%，则无法达到此目标。",

        "extra_credit_possible": "如果允许超过100分，则可能达到此目标。",

        "need_average": (
            "剩余 {remaining} 个作业需要平均达到 {needed:.2f}%。"
        ),

        "need_over_100": "需要平均达到 {needed:.2f}%。",

        "no_path": "无法根据这些数值生成可实现的成绩路径。",

        "target_average": "目标平均分",
        "average_needed": "所需平均分",

        "consistent": "稳定路径",
        "strong_finish": "强势收尾",
        "strong_start": "强势开局",
        "buffer": "缓冲路径",
        "assignment": "作业",

        "feedback_a": "表现优秀！您目前处于A等级。",
        "feedback_b": "表现不错。更高的成绩可以帮助您接近A等级。",
        "feedback_c": "您目前及格，但更好的后续成绩可以明显提高平均分。",
        "feedback_d": "当前成绩存在风险。请重点关注后续作业和额外加分。",
        "feedback_f": "当前平均分低于及格水平。请重点提高后续作业成绩。",

        "below_target": (
            "您比 {target:.2f}% 的目标低 {difference:.2f} 个百分点。"
        ),
        "above_target": "您比目标高 {difference:.2f} 个百分点。",
        "at_target": "您正好达到目标。",
    },
}


# =========================================================
# THEMES
# =========================================================

LIGHT_THEME = {
    "background": (0.94, 0.95, 0.97, 1),
    "card": (1, 1, 1, 1),
    "text": (0.08, 0.10, 0.14, 1),
    "secondary_text": (0.35, 0.38, 0.44, 1),
    "input": (0.96, 0.97, 0.98, 1),
    "disabled_input": (0.88, 0.89, 0.91, 1),
    "primary": (0.16, 0.43, 0.78, 1),
    "selected": (0.16, 0.43, 0.78, 1),
    "unselected": (0.86, 0.88, 0.91, 1),
    "secondary_button": (0.82, 0.84, 0.87, 1),
    "button_text": (1, 1, 1, 1),
}


DARK_THEME = {
    "background": (0.06, 0.07, 0.09, 1),
    "card": (0.11, 0.12, 0.15, 1),
    "text": (0.95, 0.96, 0.98, 1),
    "secondary_text": (0.68, 0.71, 0.77, 1),
    "input": (0.16, 0.17, 0.20, 1),
    "disabled_input": (0.11, 0.12, 0.14, 1),
    "primary": (0.22, 0.50, 0.88, 1),
    "selected": (0.22, 0.50, 0.88, 1),
    "unselected": (0.22, 0.24, 0.28, 1),
    "secondary_button": (0.25, 0.27, 0.31, 1),
    "button_text": (1, 1, 1, 1),
}


# =========================================================
# SYSTEM THEME
# =========================================================

def system_uses_dark_mode() -> bool:
    """Read Android system light/dark setting."""

    if platform != "android":
        return False

        try:
            from jnius import autoclass

            PythonActivity = autoclass(
                "org.kivy.android.PythonActivity"
            )

            activity = PythonActivity.mActivity

            configuration = (
                activity
                .getResources()
                .getConfiguration()
            )

            return (
                configuration.uiMode & 0x30
            ) == 0x20

        except Exception:
            return False


# =========================================================
# TRANSLATED FEEDBACK
# =========================================================

def translated_feedback(
    average: float,
    lang: dict,
    target: float | None = None,
) -> str:
    """Return progress feedback in the selected language."""

    if average >= 90:
        message = lang["feedback_a"]

    elif average >= 80:
        message = lang["feedback_b"]

    elif average >= 70:
        message = lang["feedback_c"]

    elif average >= 60:
        message = lang["feedback_d"]

    else:
        message = lang["feedback_f"]

    if target is not None:

        difference = target - average

        if difference > 0:
            message += (
                "\n\n"
                + lang["below_target"].format(
                    difference=difference,
                    target=target,
                )
            )

        elif difference < 0:
            message += (
                "\n\n"
                + lang["above_target"].format(
                    difference=abs(difference)
                )
            )

        else:
            message += (
                "\n\n"
                + lang["at_target"]
            )

    return message


# =========================================================
# CUSTOM UI
# =========================================================

class Card(BoxLayout):
    """Rounded mobile content card."""

    radius = NumericProperty(dp(18))

    def __init__(self, **kwargs):

        super().__init__(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(16),
            size_hint_y=None,
            **kwargs,
        )

        self.bind(
            minimum_height=self.setter("height")
        )

        with self.canvas.before:

            self.card_color = Color(
                1,
                1,
                1,
                1,
            )

            self.card_rectangle = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.radius],
            )

        self.bind(
            pos=self.update_background,
            size=self.update_background,
        )

    def update_background(self, *args):

        self.card_rectangle.pos = self.pos
        self.card_rectangle.size = self.size

    def set_color(self, color):

        self.card_color.rgba = color


class RoundedButton(Button):
    """Rounded action button."""

    def __init__(self, **kwargs):

        super().__init__(
            size_hint_y=None,
            height=dp(54),
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            **kwargs,
        )

        with self.canvas.before:

            self.button_color = Color(
                0.16,
                0.43,
                0.78,
                1,
            )

            self.button_rectangle = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(14)],
            )

        self.bind(
            pos=self.update_background,
            size=self.update_background,
        )

    def update_background(self, *args):

        self.button_rectangle.pos = self.pos
        self.button_rectangle.size = self.size

    def set_color(self, color):

        self.button_color.rgba = color


class SelectableButton(Button):
    """Tap-to-select highlighted button."""

    def __init__(self, **kwargs):

        super().__init__(
            size_hint_y=None,
            height=dp(52),
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            **kwargs,
        )

        self.selected = False

        with self.canvas.before:

            self.button_color = Color(
                0.86,
                0.88,
                0.91,
                1,
            )

            self.button_rectangle = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(14)],
            )

        self.bind(
            pos=self.update_background,
            size=self.update_background,
        )

        self.bind(
            on_press=self.toggle_selected
        )

    def update_background(self, *args):

        self.button_rectangle.pos = self.pos
        self.button_rectangle.size = self.size

    def toggle_selected(self, *args):

        self.selected = not self.selected

        app = App.get_running_app()

        if (
            app is not None
            and isinstance(
                app.root,
                ScrollView,
            )
            and app.root.children
        ):

            layout = app.root.children[0]

            layout.apply_system_theme()

    def set_selected(
        self,
        value: bool,
    ):

        self.selected = value

    def set_color(self, color):

        self.button_color.rgba = color


# =========================================================
# MAIN APP INTERFACE
# =========================================================

class GradeCalculatorAndroid(BoxLayout):
    """Main Android calculator interface."""

    def __init__(self, **kwargs):

        super().__init__(
            orientation="vertical",
            spacing=dp(14),
            padding=dp(14),
            size_hint_y=None,
            **kwargs,
        )

        self.bind(
            minimum_height=self.setter("height")
        )

        self.current_grades: list[float] = []

        self.current_language = "English"

        self.is_dark_mode = (
            system_uses_dark_mode()
        )

        self.load_preferences()

        self.build_header()
        self.build_student_card()
        self.build_current_card()
        self.build_goal_card()
        self.build_path_card()
        self.build_about_card()
        self.build_reset_button()

        self.apply_language()
        self.apply_system_theme()

        Clock.schedule_interval(
            self.check_system_theme,
            2,
        )


    # =====================================================
    # UI BUILDING
    # =====================================================

    def build_header(self):

        self.header_card = Card()

        self.title_label = Label(
            font_size="25sp",
            bold=True,
            size_hint_y=None,
            height=dp(50),
        )

        self.subtitle_label = Label(
            font_size="14sp",
            size_hint_y=None,
            height=dp(30),
        )

        language_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50),
        )

        self.language_label = Label(
            size_hint_x=0.4,
        )

        self.language_spinner = Spinner(
            text=self.current_language,
            values=list(
                LANGUAGES.keys()
            ),
            size_hint_x=0.6,
        )

        self.language_spinner.bind(
            text=self.change_language
        )

        language_row.add_widget(
            self.language_label
        )

        language_row.add_widget(
            self.language_spinner
        )

        self.header_card.add_widget(
            self.title_label
        )

        self.header_card.add_widget(
            self.subtitle_label
        )

        self.header_card.add_widget(
            language_row
        )

        self.add_widget(
            self.header_card
        )



    def build_student_card(self):
        """Build one grade-entry area for Standard or Weighted grading."""

        self.student_card = Card()

        self.student_heading = Label(
            bold=True,
            font_size="19sp",
            size_hint_y=None,
            height=dp(38),
        )

        self.name_label = Label(
            size_hint_y=None,
            height=dp(26),
        )

        self.name_input = self.create_input()

        self.grading_mode_label = Label(
            text="How is this course graded?",
            size_hint_y=None,
            height=dp(26),
        )

        self.grading_mode_spinner = Spinner(
            text="Standard",
            values=("Standard", "Weighted"),
            size_hint_y=None,
            height=dp(50),
        )

        self.grading_mode_spinner.bind(
            text=self.update_grading_mode
        )

        # Standard grade-entry controls.
        self.grades_label = Label(
            size_hint_y=None,
            height=dp(26),
        )

        self.grades_input = self.create_input()

        self.allow_over_100 = SelectableButton()
        self.use_extra_credit = SelectableButton()

        self.extra_points_label = Label(
            size_hint_y=None,
            height=dp(26),
        )

        self.extra_credit_input = self.create_input(
            text="0",
            input_filter="float",
        )

        # Weighted grade-entry controls.
        self.weighted_instructions = Label(
            text=(
                "Enter grades for each category, then enter "
                "the percentage that category is worth."
            ),
            size_hint_y=None,
            height=dp(65),
            halign="center",
            valign="middle",
        )
        self.weighted_instructions.bind(
            width=lambda widget, width: setattr(
                widget,
                "text_size",
                (width - dp(20), None),
            )
        )

        self.tests_label = Label(
            text="Tests",
            bold=True,
            size_hint_y=None,
            height=dp(26),
        )
        self.tests_grades = self.create_input()
        self.tests_grades.hint_text = "Grades: 85, 92, 78"
        self.tests_weight_label = Label(
            text="Tests Weight (%)",
            size_hint_y=None,
            height=dp(26),
        )
        self.tests_weight = self.create_input(
            input_filter="float"
        )
        self.tests_weight.hint_text = "Example: 40"

        self.quizzes_label = Label(
            text="Quizzes",
            bold=True,
            size_hint_y=None,
            height=dp(26),
        )
        self.quizzes_grades = self.create_input()
        self.quizzes_grades.hint_text = "Grades: 90, 88"
        self.quizzes_weight_label = Label(
            text="Quizzes Weight (%)",
            size_hint_y=None,
            height=dp(26),
        )
        self.quizzes_weight = self.create_input(
            input_filter="float"
        )
        self.quizzes_weight.hint_text = "Example: 25"

        self.homework_label = Label(
            text="Homework",
            bold=True,
            size_hint_y=None,
            height=dp(26),
        )
        self.homework_grades = self.create_input()
        self.homework_grades.hint_text = "Grades: 100, 95, 92"
        self.homework_weight_label = Label(
            text="Homework Weight (%)",
            size_hint_y=None,
            height=dp(26),
        )
        self.homework_weight = self.create_input(
            input_filter="float"
        )
        self.homework_weight.hint_text = "Example: 35"

        self.calculate_button = RoundedButton()
        self.calculate_button.bind(
            on_press=self.calculate_grade
        )

        self.update_grading_mode(
            self.grading_mode_spinner,
            "Standard",
        )

        self.add_widget(
            self.student_card
        )


    def update_grading_mode(
        self,
        spinner,
        mode,
    ):
        """Switch the existing grade-entry area between Standard and Weighted."""

        if not hasattr(self, "student_card"):
            return

        self.student_card.clear_widgets()

        common_widgets = [
            self.student_heading,
            self.name_label,
            self.name_input,
            self.grading_mode_label,
            self.grading_mode_spinner,
        ]

        for widget in common_widgets:
            self.student_card.add_widget(widget)

        if mode == "Weighted":
            weighted_widgets = [
                self.weighted_instructions,
                self.tests_label,
                self.tests_grades,
                self.tests_weight_label,
                self.tests_weight,
                self.quizzes_label,
                self.quizzes_grades,
                self.quizzes_weight_label,
                self.quizzes_weight,
                self.homework_label,
                self.homework_grades,
                self.homework_weight_label,
                self.homework_weight,
                self.allow_over_100,
            ]

            for widget in weighted_widgets:
                self.student_card.add_widget(widget)

        else:
            standard_widgets = [
                self.grades_label,
                self.grades_input,
                self.allow_over_100,
                self.use_extra_credit,
                self.extra_points_label,
                self.extra_credit_input,
            ]

            for widget in standard_widgets:
                self.student_card.add_widget(widget)

        self.student_card.add_widget(
            self.calculate_button
        )

        # Clear stale calculated results when the grading method changes.
        self.current_grades = []

        if hasattr(self, "result_label"):
            lang = self.lang()
            self.result_label.text = (
                f"{lang['average']}: --\n"
                f"{lang['letter_grade']}: --"
            )
            self.feedback_label.text = ""

        if hasattr(self, "path_results"):
            self.path_results.text = (
                self.lang()["path_placeholder"]
            )

        if hasattr(self, "current_card"):
            self.apply_system_theme()


    def build_current_card(self):

        self.current_card = Card()

        self.current_heading = Label(
            bold=True,
            font_size="19sp",
            size_hint_y=None,
            height=dp(38),
        )

        self.result_label = Label(
            font_size="21sp",
            bold=True,
            size_hint_y=None,
            height=dp(75),
        )

        self.feedback_label = Label(
            size_hint_y=None,
            height=dp(125),
            halign="center",
            valign="middle",
        )

        self.feedback_label.bind(
            width=lambda widget, width:
            setattr(
                widget,
                "text_size",
                (width - dp(20), None),
            )
        )

        self.current_card.add_widget(
            self.current_heading
        )

        self.current_card.add_widget(
            self.result_label
        )

        self.current_card.add_widget(
            self.feedback_label
        )

        self.add_widget(
            self.current_card
        )


    def build_goal_card(self):

        self.goal_card = Card()

        self.goal_heading = Label(
            bold=True,
            font_size="19sp",
            size_hint_y=None,
            height=dp(38),
        )

        self.target_label = Label(
            size_hint_y=None,
            height=dp(26),
        )

        self.target_input = (
            self.create_input(
                input_filter="float"
            )
        )

        self.remaining_label = Label(
            size_hint_y=None,
            height=dp(26),
        )

        self.remaining_input = (
            self.create_input(
                input_filter="int"
            )
        )

        self.goal_button = RoundedButton()

        self.goal_button.bind(
            on_press=self.calculate_goal
        )

        self.goal_label = Label(
            size_hint_y=None,
            height=dp(105),
            halign="center",
            valign="middle",
        )

        self.goal_label.bind(
            width=lambda widget, width:
            setattr(
                widget,
                "text_size",
                (width - dp(20), None),
            )
        )

        for widget in [
            self.goal_heading,
            self.target_label,
            self.target_input,
            self.remaining_label,
            self.remaining_input,
            self.goal_button,
            self.goal_label,
        ]:

            self.goal_card.add_widget(
                widget
            )

        self.add_widget(
            self.goal_card
        )


    def build_path_card(self):
        """Build the Grade Path Planning card.

        The results label expands with its content so the main page
        ScrollView handles scrolling. This avoids nested-scroll issues
        that can make the About and Reset sections feel unreachable.
        """

        self.path_card = Card()

        self.path_heading = Label(
            bold=True,
            font_size="19sp",
            size_hint_y=None,
            height=dp(38),
        )

        self.path_button = RoundedButton()

        self.path_button.bind(
            on_press=self.show_grade_paths
        )

        self.path_results = Label(
            size_hint_y=None,
            halign="left",
            valign="top",
            padding=(
                dp(10),
                dp(10),
            ),
        )

        self.path_results.bind(
            width=lambda widget, width: setattr(
                widget,
                "text_size",
                (width - dp(20), None),
            )
        )

        self.path_results.bind(
            texture_size=lambda widget, size: setattr(
                widget,
                "height",
                max(dp(170), size[1] + dp(24)),
            )
        )

        self.path_card.add_widget(
            self.path_heading
        )

        self.path_card.add_widget(
            self.path_button
        )

        self.path_card.add_widget(
            self.path_results
        )

        self.add_widget(
            self.path_card
        )


    def build_about_card(self):
        """Build the About Grade Assist card."""

        self.about_card = Card()

        self.about_heading = Label(
            text=f"About {APP_NAME}",
            bold=True,
            font_size="19sp",
            size_hint_y=None,
            height=dp(38),
        )

        self.about_text = Label(
            text=(
                f"{APP_NAME}\n\n"
                f"Version {APP_VERSION}\n\n"
                f"{TAGLINE}\n\n"
                "Grade Assist helps students calculate averages, "
                "plan target grades, explore grade paths, and "
                "account for extra credit."
            ),
            size_hint_y=None,
            height=dp(210),
            halign="center",
            valign="middle",
        )

        self.about_text.bind(
            width=lambda widget, width: setattr(
                widget,
                "text_size",
                (width - dp(20), None),
            )
        )

        self.about_card.add_widget(
            self.about_heading
        )

        self.about_card.add_widget(
            self.about_text
        )

        self.add_widget(
            self.about_card
        )


    def build_reset_button(self):

        self.clear_button = RoundedButton()

        self.clear_button.bind(
            on_press=self.clear
        )

        self.add_widget(
            self.clear_button
        )


    def create_input(
        self,
        text="",
        input_filter=None,
    ):

        field = TextInput(
            text=text,
            multiline=False,
            input_filter=input_filter,
            size_hint_y=None,
            height=dp(50),
            padding=(
                dp(12),
                dp(13),
            ),
        )

        field.background_normal = ""
        field.background_active = ""

        return field


    # =====================================================
    # LANGUAGE
    # =====================================================

    def lang(self):

        return LANGUAGES[
            self.current_language
        ]


    def change_language(
        self,
        spinner,
        language_name,
    ):

        if language_name not in LANGUAGES:
            return

        self.current_language = (
            language_name
        )

        self.apply_language()

        self.save_preferences()



    def apply_language(self):

        lang = self.lang()

        self.title_label.text = (
            lang["title"]
        )

        self.subtitle_label.text = (
            lang["subtitle"]
        )

        self.language_label.text = (
            lang["language"]
        )

        self.student_heading.text = (
            lang["student_section"]
        )

        self.name_label.text = (
            lang["student_name"]
        )

        self.grading_mode_label.text = (
            "How is this course graded?"
        )

        self.grades_label.text = (
            lang["grades"]
        )

        self.grades_input.hint_text = (
            lang["grades_hint"]
        )

        self.allow_over_100.text = (
            lang["allow_over_100"]
        )

        self.use_extra_credit.text = (
            lang["use_extra_credit"]
        )

        self.extra_points_label.text = (
            lang["extra_credit"]
        )

        self.calculate_button.text = (
            lang["calculate"]
        )

        self.current_heading.text = (
            lang["current_results"]
        )

        self.goal_heading.text = (
            lang["goal_section"]
        )

        self.target_label.text = (
            lang["desired_grade"]
        )

        self.target_input.hint_text = (
            lang["target_hint"]
        )

        self.remaining_label.text = (
            lang["remaining"]
        )

        self.remaining_input.hint_text = (
            lang["remaining_hint"]
        )

        self.goal_button.text = (
            lang["goal"]
        )

        self.path_heading.text = (
            lang["path_results"]
        )

        self.path_button.text = (
            lang["path"]
        )

        self.clear_button.text = (
            lang["clear"]
        )

        if not self.current_grades:

            self.result_label.text = (
                f"{lang['average']}: --\n"
                f"{lang['letter_grade']}: --"
            )

            self.path_results.text = (
                lang["path_placeholder"]
            )


    # =====================================================
    # THEME
    # =====================================================

    def check_system_theme(
        self,
        dt,
    ):

        current = (
            system_uses_dark_mode()
        )

        if current != self.is_dark_mode:

            self.is_dark_mode = current

            self.apply_system_theme()



    def apply_system_theme(self):

        theme = (
            DARK_THEME
            if self.is_dark_mode
            else LIGHT_THEME
        )

        Window.clearcolor = (
            theme["background"]
        )

        for card in [
            self.header_card,
            self.student_card,
            self.current_card,
            self.goal_card,
            self.path_card,
            self.about_card,
        ]:

            card.set_color(
                theme["card"]
            )

        for label in [
            self.title_label,
            self.student_heading,
            self.current_heading,
            self.goal_heading,
            self.path_heading,
            self.about_heading,
            self.result_label,
            self.tests_label,
            self.quizzes_label,
            self.homework_label,
        ]:

            label.color = (
                theme["text"]
            )

        for label in [
            self.subtitle_label,
            self.language_label,
            self.name_label,
            self.grading_mode_label,
            self.grades_label,
            self.extra_points_label,
            self.weighted_instructions,
            self.tests_weight_label,
            self.quizzes_weight_label,
            self.homework_weight_label,
            self.feedback_label,
            self.target_label,
            self.remaining_label,
            self.goal_label,
            self.path_results,
            self.about_text,
        ]:

            label.color = (
                theme["secondary_text"]
            )

        for field in [
            self.name_input,
            self.grades_input,
            self.tests_grades,
            self.tests_weight,
            self.quizzes_grades,
            self.quizzes_weight,
            self.homework_grades,
            self.homework_weight,
            self.target_input,
            self.remaining_input,
        ]:

            field.background_color = (
                theme["input"]
            )

            field.foreground_color = (
                theme["text"]
            )

            field.cursor_color = (
                theme["text"]
            )

            field.hint_text_color = (
                theme["secondary_text"]
            )

        for button in [
            self.calculate_button,
            self.goal_button,
            self.path_button,
        ]:

            button.set_color(
                theme["primary"]
            )

            button.color = (
                theme["button_text"]
            )

        for button in [
            self.allow_over_100,
            self.use_extra_credit,
        ]:

            if button.selected:

                button.set_color(
                    theme["selected"]
                )

                button.color = (
                    theme["button_text"]
                )

            else:

                button.set_color(
                    theme["unselected"]
                )

                button.color = (
                    theme["text"]
                )

        self.clear_button.set_color(
            theme["secondary_button"]
        )

        self.clear_button.color = (
            theme["text"]
        )

        for spinner in [
            self.language_spinner,
            self.grading_mode_spinner,
        ]:
            spinner.background_normal = ""
            spinner.background_color = (
                theme["input"]
            )
            spinner.color = (
                theme["text"]
            )

        self.update_extra_credit_field()


    # =====================================================
    # INPUT VALIDATION
    # =====================================================

    def parse_mobile_grades(self):

        lang = self.lang()

        raw = (
            self.grades_input
            .text
            .strip()
        )

        if not raw:

            raise ValueError(
                lang["missing_grades"]
            )

        for item in raw.split(","):

            value = item.strip()

            if not value:

                raise ValueError(
                    lang["blank_grade"]
                )

            try:
                number = float(value)

            except ValueError:

                raise ValueError(
                    lang["invalid_grade"].format(
                        value=value
                    )
                )

            if number < 0:

                raise ValueError(
                    lang["negative_grade"]
                )

            if (
                number > 100
                and not self.allow_over_100.selected
            ):

                raise ValueError(
                    lang["over_100_error"]
                )

        return parse_grades(
            raw,
            self.allow_over_100.selected,
        )


    def get_extra_credit(self):

        lang = self.lang()

        if not self.use_extra_credit.selected:
            return 0.0

        raw = (
            self.extra_credit_input
            .text
            .strip()
        )

        if not raw:
            return 0.0

        try:

            points = float(raw)

        except ValueError:

            raise ValueError(
                lang["invalid_extra_credit"]
            )

        if points < 0:

            raise ValueError(
                lang["extra_credit_negative"]
            )

        return points


    def get_goal_values(self):

        lang = self.lang()

        target_text = (
            self.target_input
            .text
            .strip()
        )

        if not target_text:

            raise ValueError(
                lang["enter_target"]
            )

        try:

            target = float(
                target_text
            )

        except ValueError:

            raise ValueError(
                lang["invalid_target"]
            )

        if not 0 <= target <= 100:

            raise ValueError(
                lang["invalid_target"]
            )

        remaining_text = (
            self.remaining_input
            .text
            .strip()
        )

        if not remaining_text:

            raise ValueError(
                lang["enter_remaining"]
            )

        try:

            remaining = int(
                remaining_text
            )

        except ValueError:

            raise ValueError(
                lang["invalid_remaining"]
            )

        if remaining <= 0:

            raise ValueError(
                lang["invalid_remaining"]
            )

        return target, remaining


    # =====================================================
    # EXTRA CREDIT STATE
    # =====================================================


    def update_extra_credit_field(self):

        theme = (
            DARK_THEME
            if self.is_dark_mode
            else LIGHT_THEME
        )

        standard_mode = (
            self.grading_mode_spinner.text
            == "Standard"
        )

        enabled = (
            standard_mode
            and self.use_extra_credit.selected
        )

        self.extra_credit_input.disabled = (
            not enabled
        )

        if enabled:

            self.extra_credit_input.background_color = (
                theme["input"]
            )

            self.extra_credit_input.foreground_color = (
                theme["text"]
            )

        else:

            self.extra_credit_input.background_color = (
                theme["disabled_input"]
            )

            self.extra_credit_input.foreground_color = (
                theme["secondary_text"]
            )


    # =====================================================
    # RESULTS / ERRORS
    # =====================================================

    def show_message(
        self,
        message,
    ):

        self.path_results.text = (
            message
        )



    # =====================================================
    # CALCULATE CURRENT GRADE
    # =====================================================


    def calculate_grade(
        self,
        instance,
    ):

        lang = self.lang()

        if not (
            self.name_input
            .text
            .strip()
        ):

            self.show_message(
                lang["missing_name"]
            )

            return

        try:

            if (
                self.grading_mode_spinner.text
                == "Weighted"
            ):
                categories = []

                weighted_inputs = [
                    (
                        "Tests",
                        self.tests_grades,
                        self.tests_weight,
                    ),
                    (
                        "Quizzes",
                        self.quizzes_grades,
                        self.quizzes_weight,
                    ),
                    (
                        "Homework",
                        self.homework_grades,
                        self.homework_weight,
                    ),
                ]

                for (
                    category_name,
                    grades_input,
                    weight_input,
                ) in weighted_inputs:

                    grades_text = (
                        grades_input.text.strip()
                    )

                    weight_text = (
                        weight_input.text.strip()
                    )

                    if (
                        not grades_text
                        and not weight_text
                    ):
                        continue

                    if (
                        not grades_text
                        or not weight_text
                    ):
                        raise ValueError(
                            f"Enter both grades and a "
                            f"weight for {category_name}."
                        )

                    grades = parse_grades(
                        grades_text,
                        allow_over_100=(
                            self.allow_over_100.selected
                        ),
                    )

                    try:
                        weight = float(
                            weight_text
                        )
                    except ValueError as exc:
                        raise ValueError(
                            f"{category_name} weight "
                            f"must be a valid number."
                        ) from exc

                    if weight < 0:
                        raise ValueError(
                            "Category weights "
                            "cannot be negative."
                        )

                    categories.append(
                        (grades, weight)
                    )

                average = (
                    calculate_weighted_average(
                        categories
                    )
                )

                # Grade Goal and Grade Path currently use
                # individual standard grades, so do not
                # feed them stale unweighted data.
                self.current_grades = []

            else:

                grades = (
                    self.parse_mobile_grades()
                )

                extra_credit = (
                    self.get_extra_credit()
                )

                average = calculate_average(
                    grades,
                    extra_credit,
                )

                self.current_grades = grades

        except ValueError as error:

            self.show_message(
                str(error)
            )

            return

        self.result_label.text = (
            f"{lang['average']}: "
            f"{average:.2f}%\n"
            f"{lang['letter_grade']}: "
            f"{letter_grade(average)}"
        )

        self.feedback_label.text = (
            translated_feedback(
                average,
                lang,
            )
        )


    # =====================================================
    # GRADE GOAL
    # =====================================================

    def calculate_goal(
        self,
        instance,
    ):

        lang = self.lang()

        if not self.current_grades:

            self.show_message(
                lang["calculate_first"]
            )

            return

        try:

            target, remaining = (
                self.get_goal_values()
            )

            extra_credit = (
                self.get_extra_credit()
            )

            needed = calculate_required_grade(
                self.current_grades,
                target,
                remaining,
                extra_credit,
            )

            current_average = (
                calculate_average(
                    self.current_grades,
                    extra_credit,
                )
            )

        except ValueError as error:

            self.show_message(
                str(error)
            )

            return

        if needed > 100:

            result = (
                lang["need_over_100"].format(
                    needed=needed
                )
            )

            if self.allow_over_100.selected:

                result += (
                    "\n\n"
                    + lang[
                        "extra_credit_possible"
                    ]
                )

            else:

                result += (
                    "\n\n"
                    + lang[
                        "not_achievable"
                    ]
                )

        elif needed <= 0:

            result = (
                lang["goal_secured"]
            )

        else:

            result = (
                lang["need_average"].format(
                    needed=needed,
                    remaining=remaining,
                )
            )

        self.goal_label.text = (
            result
        )

        self.feedback_label.text = (
            translated_feedback(
                current_average,
                lang,
                target,
            )
        )


    # =====================================================
    # GRADE PATH PLANNING
    # =====================================================

    def show_grade_paths(
        self,
        instance,
    ):

        lang = self.lang()

        if not self.current_grades:

            self.show_message(
                lang["calculate_first"]
            )

            return

        try:

            target, remaining = (
                self.get_goal_values()
            )

            extra_credit = (
                self.get_extra_credit()
            )

            needed = calculate_required_grade(
                self.current_grades,
                target,
                remaining,
                extra_credit,
            )

            paths = generate_grade_paths(
                self.current_grades,
                target,
                remaining,
                extra_credit,
                self.allow_over_100.selected,
            )

        except ValueError as error:

            self.show_message(
                str(error)
            )

            return

        if not paths:

            self.path_results.text = (
                f"{lang['target_average']}: "
                f"{target:.2f}%\n\n"
                f"{lang['average_needed']}: "
                f"{needed:.2f}%\n\n"
                f"{lang['no_path']}"
            )

            return

        path_names = [
            lang["consistent"],
            lang["strong_finish"],
            lang["strong_start"],
            lang["buffer"],
        ]

        lines = [
            f"{lang['target_average']}: "
            f"{target:.2f}%",
            "",
            f"{lang['remaining']}: "
            f"{remaining}",
            "",
            f"{lang['average_needed']}: "
            f"{needed:.2f}%",
            "",
        ]

        for index, path in enumerate(
            paths
        ):

            if index < len(
                path_names
            ):

                title = (
                    path_names[index]
                )

            else:

                title = (
                    f"Path {index + 1}"
                )

            lines.append(title)

            lines.append(
                "─" * 20
            )

            for (
                assignment_number,
                score,
            ) in enumerate(
                path,
                start=1,
            ):

                lines.append(
                    f"{lang['assignment']} "
                    f"{assignment_number}: "
                    f"{score}%"
                )

            lines.append("")
            lines.append("")

        self.path_results.text = (
            "\n".join(lines)
        )



    # =====================================================
    # RESET
    # =====================================================


    def clear(
        self,
        instance,
    ):

        lang = self.lang()

        self.name_input.text = ""

        self.grades_input.text = ""

        self.tests_grades.text = ""
        self.tests_weight.text = ""

        self.quizzes_grades.text = ""
        self.quizzes_weight.text = ""

        self.homework_grades.text = ""
        self.homework_weight.text = ""

        self.target_input.text = ""

        self.remaining_input.text = ""

        self.extra_credit_input.text = "0"

        self.allow_over_100.set_selected(
            False
        )

        self.use_extra_credit.set_selected(
            False
        )

        self.grading_mode_spinner.text = (
            "Standard"
        )

        self.current_grades = []

        self.result_label.text = (
            f"{lang['average']}: --\n"
            f"{lang['letter_grade']}: --"
        )

        self.feedback_label.text = ""

        self.goal_label.text = ""

        self.path_results.text = (
            lang["path_placeholder"]
        )

        self.update_grading_mode(
            self.grading_mode_spinner,
            "Standard",
        )

        self.apply_system_theme()



    # =====================================================
    # SAVED LANGUAGE
    # =====================================================

    def preferences_path(self):

        app = App.get_running_app()

        if app is not None:

            return (
                Path(
                    app.user_data_dir
                )
                / "preferences.json"
            )

        return Path(
            "android_preferences.json"
        )


    def save_preferences(self):

        try:

            path = (
                self.preferences_path()
            )

            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with path.open(
                "w",
                encoding="utf-8",
            ) as file:

                json.dump(
                    {
                        "language":
                            self.current_language
                    },
                    file,
                    ensure_ascii=False,
                    indent=4,
                )

        except OSError:
            pass


    def load_preferences(self):

        try:

            path = (
                self.preferences_path()
            )

            if not path.exists():
                return

            with path.open(
                "r",
                encoding="utf-8",
            ) as file:

                preferences = (
                    json.load(file)
                )

            language = (
                preferences.get(
                    "language",
                    "English",
                )
            )

            if language in LANGUAGES:

                self.current_language = (
                    language
                )

        except (
            OSError,
            json.JSONDecodeError,
        ):
            pass


# =========================================================
# APPLICATION
# =========================================================

class GradeCalculatorAndroidApp(App):
    """Android Student Grade Calculator."""

    def build(self):

        self.title = APP_NAME

        layout = (
            GradeCalculatorAndroid()
        )

        scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(6),
            scroll_type=["bars", "content"],
        )

        scroll.add_widget(
            layout
        )

        return scroll


if __name__ == "__main__":
    GradeCalculatorAndroidApp().run()
