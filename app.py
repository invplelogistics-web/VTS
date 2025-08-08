import streamlit as st
import fitz  # PyMuPDF
import io

# Chuyển màu integer sang tuple RGB (0-1)
def int_to_rgb_tuple(color_int):
    r = ((color_int >> 16) & 255) / 255
    g = ((color_int >> 8) & 255) / 255
    b = (color_int & 255) / 255
    return (r, g, b)

st.set_page_config(page_title="PDF Text Replace", page_icon="📝")
st.title("🔄 Thay thế văn bản trong PDF (giữ vị trí, size & màu chữ)")

uploaded_file = st.file_uploader("📄 Tải file PDF", type=["pdf"])
old_text = st.text_input("Chuỗi cần thay thế", value="VIETCARE MADRID 2018 S.L")
new_text = st.text_input("Chuỗi thay thế", value="SUNFLOWER LOGISTIC SL")

if uploaded_file and old_text and new_text:
    if st.button("Thay thế và tải PDF"):
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        replace_count = 0

        for page in doc:
            text_dict = page.get_text("dict")["blocks"]
            for block in text_dict:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            if old_text in span["text"]:
                                rects = page.search_for(span["text"])
                                for rect in rects:
                                    # Che chữ cũ
                                    page.add_redact_annot(rect, fill=(1, 1, 1))
                                page.apply_redactions()

                                # Viết chữ mới vào đúng vùng cũ, căn trái
                                for rect in rects:
                                    page.insert_textbox(
                                        rect,
                                        span["text"].replace(old_text, new_text),
                                        fontsize=span["size"],
                                        fontname="helv",  # Font chuẩn để tránh lỗi
                                        color=int_to_rgb_tuple(span["color"]),
                                        align=0  # 0 = căn trái
                                    )
                                    replace_count += 1

        # Xuất PDF mới ra bộ nhớ
        output_bytes = io.BytesIO()
        doc.save(output_bytes)
        doc.close()
        output_bytes.seek(0)

        st.success(f"✅ Đã thay thế {replace_count} lần!")
        st.download_button(
            label="⬇️ Tải PDF đã sửa",
            data=output_bytes,
            file_name="pdf_thay_the.pdf",
            mime="application/pdf"
        )
