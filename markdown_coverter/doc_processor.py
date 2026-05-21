import logging
import re
from pathlib import Path
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling.models.factories.base_factory import BaseFactory
from markdown_coverter.vn_doc_converter import VietnameseOcrOptions, VietnameseOcrModel

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
_log = logging.getLogger(__name__)


class DocProcessor:
    def __init__(self):
        self._apply_factory_patch()
        _log.info("DocProcessor đã được khởi tạo và cấu hình hệ thống.")

    def _apply_factory_patch(self):
        original_create_instance = BaseFactory.create_instance

        def patched_create_instance(factory_self, options, **kwargs):
            if isinstance(options, VietnameseOcrOptions):
                if 'enabled' not in kwargs:
                    kwargs['enabled'] = True
                return VietnameseOcrModel(options=options, **kwargs)

            return original_create_instance(factory_self, options, **kwargs)

        BaseFactory.create_instance = patched_create_instance

    def clean_vietnamese_markdown(self, md_text: str) -> str:
        if not md_text:
            return ""

        lower_vn_chars = 'a-zđàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹ'

        # 0. DỌN SỐ TRANG (Sửa đúng lỗi: Tránh số trang gộp vào dòng dưới thành "6 b)")
        md_text = re.sub(r'^\s*\d+\s*$\n+', '', md_text, flags=re.MULTILINE)

        # 1. SỬA LỖI DOCLING TỰ NGẮT DÒNG VÀ CHÈN SỐ (Sửa đúng lỗi: Tránh gộp "hiện a)")
        md_text = re.sub(
            fr'([^\n.:])\n\s*(?:-\s*)?(?:\d+\.\s+)?(["“”]?\s*[{lower_vn_chars}])(?!\))',
            r'\1 \2',
            md_text
        )

        # ==========================================================
        # 2. XỬ LÝ LỖI OCR ĐỌC DÍNH VÀ SỐ CHỒNG SỐ CƠ BẢN
        # ==========================================================
        md_text = re.sub(r'^\s*\d+\.\s*(\d+)', r'\1', md_text, flags=re.MULTILINE)
        md_text = re.sub(r'(\d+)[c:]+\s*', r'\1. ', md_text)

        # ==========================================================
        # 3. CHUẨN HÓA CẤU TRÚC DANH SÁCH
        # ==========================================================
        # ---> FIX MỚI: Xóa dòng rác chỉ chứa mỗi số đếm ảo (VD: "9. \n") <---
        md_text = re.sub(r'^\s*\d+\.\s*$\n+', '', md_text, flags=re.MULTILINE)

        # ---> FIX MỚI: Xóa số đếm ảo do Docling chèn trước đoạn trích dẫn (VD: '11. "5. ' -> '"5. ') <---
        md_text = re.sub(r'^\s*\d+\.\s+(["“”]\s*[a-zA-ZđĐ0-9]+[\.\)])', r'\1', md_text, flags=re.MULTILINE)
        # -------------------------------------------------------------------------

        # Tách các danh sách bị viết liền thành đoạn (Inline lists)
        md_text = re.sub(r'([;.]\s+)(["“”]?\s*[a-zA-ZđĐ0-9]\))', r'\1\n- \2', md_text)

        # Xóa số ảo, cụm từ rác (như bM) trước điểm chữ
        md_text = re.sub(r'^\s*(?:-\s*)?\d+\.\s*(?:[a-zA-Z0-9_]{1,3}\s+)*[:;\-\.\s]*(["“”]?\s*[a-zA-ZđĐ]\))', r'\1', md_text, flags=re.MULTILINE)

        # Xóa các ký tự lót đường (1, I, i, l, !, ^...) TRƯỚC ĐIỂM CHỮ (VD: "1 a)" hoặc "^ a)" -> "a)")
        md_text = re.sub(r'^\s*(?:-\s*)?[1Iil|!i\^;:\.\-\s]*\s+(["“”]?\s*[a-zA-ZđĐ]\))', r'\1', md_text, flags=re.MULTILINE)

        # Xóa nhiễu gáy sách TRƯỚC KHOẢN SỐ (VD: "1 3." hoặc "! 4." -> "3.")
        # Bắt "1 3.", "- 1 4." hoặc "## 1 2." -> Giữ lại "3.", "- 4." và "## 2."
        md_text = re.sub(r'^(\s*(?:#+\s*)?(?:-\s*)?)[1Iil|!i\^;:\.\-]+\s+(\d+\.)', r'\1\2', md_text, flags=re.MULTILINE)

        # Xóa nhiễu rác lọt thỏm ở CUỐI DÒNG (VD: "sau đây: 1" -> "sau đây:")
        md_text = re.sub(r'([:;])\s+[1Iil|!i\^;:\.\-]\s*$', r'\1', md_text, flags=re.MULTILINE)

        # Sửa "6. : a)" hoặc "6. a)" thành "a)"
        md_text = re.sub(r'^\s*(?:-\s*)?\d+\.\s*[:;\-\.\s]*(["“”]?\s*[a-zA-ZđĐ]\))', r'\1', md_text, flags=re.MULTILINE)

        # Sửa ": a)", "- : a)" hoặc "- . a)" đứng đầu dòng thành "a)"
        md_text = re.sub(r'^\s*(?:-\s*)?[:;\-\.]\s*(["“”]?\s*[a-zA-ZđĐ0-9]\))', r'\1', md_text, flags=re.MULTILINE)

        # Xóa gạch ngang thừa trước số
        md_text = re.sub(r'^\s*-\s*(\d+\.)', r'\1', md_text, flags=re.MULTILINE)

        # Ép TẤT CẢ các điểm thành format "- x)"
        md_text = re.sub(r'^\s*(?!-)\s*(["“”]?\s*[a-zA-ZđĐ0-9]\))', r'- \1', md_text, flags=re.MULTILINE)

        # Xóa dấu hai chấm/chấm phẩy/chấm rác ngay SAU mục list
        md_text = re.sub(r'^(\s*-\s*["“”]?\s*[a-zA-ZđĐ0-9]\))\s*[:;\.]\s*', r'\1 ', md_text, flags=re.MULTILINE)

        # ==========================================================
        # 4. BỘ THEO DÕI CHUỖI KÉP (DUAL SEQUENCE TRACKER)
        # ==========================================================
        vn_alphabet = ['a', 'b', 'c', 'd', 'đ', 'e', 'g', 'h', 'i', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'x', 'y']
        expected_next_char = {vn_alphabet[i]: vn_alphabet[i + 1] for i in range(len(vn_alphabet) - 1)}

        lines = md_text.split('\n')
        current_expected_char = None
        expected_num = None

        for i, line in enumerate(lines):
            # TRACKER SỐ THỨ TỰ
            match_correct_num = re.match(r'^\s*(?:-\s*)?(\d+)\.\s+', line)
            if match_correct_num:
                expected_num = int(match_correct_num.group(1)) + 1
            else:
                match_sticky_num = re.match(r'^\s*(?:-\s*)?(\d+)\.?([A-ZÀ-Ỹ].*)', line)
                if match_sticky_num:
                    num = int(match_sticky_num.group(1))
                    text_part = match_sticky_num.group(2)
                    if expected_num and num == expected_num:
                        lines[i] = f"{num}. {text_part}"
                        expected_num = num + 1

            # TRACKER CHỮ CÁI
            match_char = re.match(r'^(\s*-\s*["“”]?\s*)([a-zđA-Z0-9])\)', line)
            if match_char:
                char = match_char.group(2).lower()
                if char in ['1', 'i'] and current_expected_char == 'l':
                    lines[i] = re.sub(r'^(\s*-\s*["“”]?\s*)[1iI]\)', r'\g<1>l)', line)
                    current_expected_char = expected_next_char.get('l')
                elif char in expected_next_char:
                    current_expected_char = expected_next_char.get(char)

        md_text = '\n'.join(lines)

        # 5. DỌN DẸP KÝ TỰ RÁC VÀ QUỐC HIỆU
        md_text = re.sub(r"^\s*(?:[a-zA-Z0-9]|[.,:;_\-|\'\"*`~]{1,2})\s*$\n+", '', md_text, flags=re.MULTILINE)
        md_text = re.sub(r'^\s*[:]\s*$', '', md_text, flags=re.MULTILINE)

        md_text = re.sub(r'^\s*-\s*(Điều\s+\d+)', r'## \1', md_text, flags=re.MULTILINE | re.IGNORECASE)
        # ---------------------------------------------------------------------------------------------

        # Bóc số đếm ảo của Docling và ép thành định dạng Heading chuẩn
        md_text = re.sub(
            r'^(?:##\s*)?\d+\.\s*(Điều\s+\d+)',
            r'## \1',
            md_text,
            flags=re.MULTILINE | re.IGNORECASE
        )

        md_text = re.sub(
            r'(CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM)\s+(Độc lập\s*-\s*Tự do\s*-\s*Hạnh phúc)',
            r'\1\n\2',
            md_text, flags=re.IGNORECASE
        )
        md_text = re.sub(
            r'##\s*(\d+\.[^\n]*?)\s*\n+\s*(?:##\s*)?Điều',
            r'## Điều \1',
            md_text, flags=re.MULTILINE | re.IGNORECASE
        )
        md_text = re.sub(r'##\s*Điều\s*\n+(?=\d+\.)', r'**Điều:** ', md_text)

        md_text = re.sub(r'\n{3,}', '\n\n', md_text)
        md_text = re.sub(r'^[ \t]+', '', md_text, flags=re.MULTILINE)

        return md_text

    def convert_pdf_to_md(self, pdf_path: str):
        pdf_path_obj = Path(pdf_path)
        if not pdf_path_obj.exists():
            _log.error(f"File không tồn tại: {pdf_path}")
            return None

        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = True

        ocr_opts = VietnameseOcrOptions()
        ocr_opts.force_full_page_ocr = True

        pipeline_options.ocr_options = ocr_opts

        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

        _log.info(f"Bắt đầu xử lý: {pdf_path_obj.name}")

        try:
            result = converter.convert(pdf_path)
            raw_md = result.document.export_to_markdown()
            clean_md = self.clean_vietnamese_markdown(raw_md)

            return clean_md

        except Exception as e:
            _log.exception(f"Lỗi trong quá trình chuyển đổi file {pdf_path}: {e}")
            return None