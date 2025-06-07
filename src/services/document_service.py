import os
from datetime import datetime
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from utils.logger import setup_logger

logger = setup_logger()

class DocumentService:
    def __init__(self):
        # Создаем директорию для документов, если её нет
        self.docs_dir = "documents"
        if not os.path.exists(self.docs_dir):
            os.makedirs(self.docs_dir)
            logger.info(f"Created documents directory at {self.docs_dir}")

    def create_docx(self, content: str, user_id: int, doc_type: str) -> str:
        """
        Создает Word документ из текста
        
        Args:
            content (str): Текст документа
            user_id (int): ID пользователя
            doc_type (str): Тип документа
            
        Returns:
            str: Путь к созданному файлу
        """
        try:
            # Создаем новый документ
            doc = Document()
            
            # Настраиваем стиль по умолчанию
            style = doc.styles['Normal']
            style.font.name = 'Times New Roman'
            style.font.size = Pt(12)
            
            # Разбиваем текст на строки
            lines = content.strip().split('\n')
            
            # Добавляем каждую строку в документ
            for line in lines:
                # Пропускаем пустые строки
                if not line.strip():
                    doc.add_paragraph()
                    continue
                    
                # Создаем параграф
                p = doc.add_paragraph()
                
                # Если это заголовок (все буквы заглавные)
                if line.strip().isupper():
                    run = p.add_run(line)
                    run.bold = True
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                else:
                    # Проверяем, является ли строка частью списка
                    if line.strip().startswith(('•', '-', '1.', '2.', '3.', '4.', '5.')):
                        p.style = 'List Bullet'
                    p.add_run(line)
                    
                    # Если это строка с датой или подписью
                    if any(keyword in line.lower() for keyword in ['дата:', 'подпись:']):
                        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            
            # Генерируем имя файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{doc_type}_{user_id}_{timestamp}.docx"
            filepath = os.path.join(self.docs_dir, filename)
            
            # Сохраняем документ
            doc.save(filepath)
            logger.info(f"Created document at {filepath}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            raise

    def delete_old_files(self, max_age_hours: int = 24):
        """
        Удаляет старые файлы из директории документов
        
        Args:
            max_age_hours (int): Максимальный возраст файлов в часах
        """
        try:
            current_time = datetime.now()
            
            for filename in os.listdir(self.docs_dir):
                filepath = os.path.join(self.docs_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                
                # Если файл старше max_age_hours часов
                if (current_time - file_time).total_seconds() > max_age_hours * 3600:
                    os.remove(filepath)
                    logger.info(f"Deleted old file: {filepath}")
                    
        except Exception as e:
            logger.error(f"Error cleaning up old files: {e}")
            # Не вызываем raise, так как это не критическая ошибка 