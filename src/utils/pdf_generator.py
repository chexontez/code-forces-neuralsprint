from fpdf import FPDF
import datetime
import os

class PDF(FPDF):
    def header(self):
        # Путь к шрифту относительно корня проекта
        font_path = os.path.join('assets', 'fonts', 'DejaVuSans.ttf')
        self.add_font('DejaVu', '', font_path, uni=True)
        self.set_font('DejaVu', '', 12)
        self.cell(0, 10, 'Отчет о тренировках NeuroSprint', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        font_path = os.path.join('assets', 'fonts', 'DejaVuSans.ttf')
        # Проверяем, был ли шрифт уже добавлен
        try:
            self.set_font('DejaVu', '', 8)
        except RuntimeError:
            self.add_font('DejaVu', '', font_path, uni=True)
            self.set_font('DejaVu', '', 8)
        self.cell(0, 10, f'Страница {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(username: str, results: list, filepath: str):
    """
    Генерирует PDF-отчет с историей тренировок.
    """
    pdf = PDF()
    pdf.add_page()
    
    # Путь к шрифту относительно корня проекта
    font_path = os.path.join('assets', 'fonts', 'DejaVuSans.ttf')
    pdf.add_font('DejaVu', '', font_path, uni=True)
    pdf.set_font('DejaVu', '', 12)

    pdf.cell(0, 10, f'Пользователь: {username}', 0, 1)
    pdf.cell(0, 10, f'Дата отчета: {datetime.date.today().strftime("%d.%m.%Y")}', 0, 1)
    pdf.ln(10)

    pdf.set_font('DejaVu', '', 10)
    pdf.cell(40, 10, 'Дата', 1)
    pdf.cell(45, 10, 'Ср. время (мс)', 1)
    pdf.cell(30, 10, 'Пропуски', 1)
    pdf.cell(45, 10, 'Ложн. нажатия', 1)
    pdf.ln()

    if not results:
        pdf.cell(0, 10, 'Нет данных для отображения.', 1, 1)
    else:
        for row in results:
            date_str = datetime.datetime.fromisoformat(row[0]).strftime('%d.%m.%y %H:%M')
            pdf.cell(40, 10, date_str, 1)
            pdf.cell(45, 10, f"{row[1]:.2f}", 1)
            pdf.cell(30, 10, str(row[2]), 1)
            pdf.cell(45, 10, str(row[3]), 1)
            pdf.ln()

    pdf.output(filepath)
    print(f"Отчет сохранен в: {filepath}")
