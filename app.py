import io
import os
import re
import tempfile
import zipfile
import streamlit as st
import tiktoken
from markitdown import MarkItDown
from ocr_helper import convert_document

st.set_page_config(
    page_title="JessMD — Doc to Markdown Converter",
    page_icon="📄",
    layout="wide"
)

@st.cache_resource
def get_converter():
    return MarkItDown()

@st.cache_resource
def get_tokenizer(encoding_name: str):
    return tiktoken.get_encoding(encoding_name)

def clean_markdown_text(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "\n".join(line.rstrip() for line in text.splitlines())
    return text.strip()

def count_tokens(text: str, tokenizer) -> int:
    return len(tokenizer.encode(text))

# --- SIDEBAR PENGATURAN ---
with st.sidebar:
    st.header("⚙️ Pengaturan Konversi")

    clean_whitespace = st.checkbox(
        "Optimasi Token (Hapus Spasi Berlebih)",
        value=True,
        help="Menghapus baris kosong beruntun dan spasi di akhir baris agar lebih hemat token."
    )

    force_ocr = st.checkbox(
        "Paksa OCR pada Semua PDF",
        value=False,
        help="Aktifkan jika PDF campuran teks dan gambar scan tidak terbaca lengkap oleh mode otomatis."
    )

    tokenizer_model = st.selectbox(
        "Standar Penghitung Token",
        options=["cl100k_base", "o200k_base"],
        index=0
    )

    st.divider()
    st.markdown(
        "**Format Didukung:**\n"
        "- Dokumen: `.pdf` (Digital & Scan OCR), `.docx`, `.txt`, `.html`\n"
        "- Presentasi: `.pptx`\n"
        "- Spreadsheet: `.xlsx`, `.xls`, `.csv`\n"
        "- Data & E-Book: `.json`, `.xml`, `.epub`"
    )

# --- HALAMAN UTAMA ---
st.title("📄 Document to Markdown Converter")
st.caption("Konversi PDF (termasuk hasil scan OCR), Word, PowerPoint, dan Excel menjadi Markdown hemat token.")

uploaded_files = st.file_uploader(
    "Unggah satu atau beberapa file sekaligus (Batch Upload)",
    type=["pdf", "docx", "pptx", "xlsx", "xls", "csv", "html", "txt", "json", "xml", "epub"],
    accept_multiple_files=True
)

if uploaded_files:
    md_converter = get_converter()
    tokenizer = get_tokenizer(tokenizer_model)

    converted_results = []
    failed_files = []

    with st.spinner("Mengonversi dokumen ke Markdown (menjalankan OCR jika PDF berupa gambar)..."):
        for uploaded_file in uploaded_files:
            suffix = os.path.splitext(uploaded_file.name)[1]
            base_name = os.path.splitext(uploaded_file.name)[0]
            md_filename = f"{base_name}.md"

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name

            try:
                md_text, used_ocr = convert_document(tmp_path, md_converter, force_ocr=force_ocr)

                if clean_whitespace:
                    md_text = clean_markdown_text(md_text)

                tokens = count_tokens(md_text, tokenizer)
                converted_results.append({
                    "original_name": uploaded_file.name,
                    "md_filename": md_filename,
                    "content": md_text,
                    "tokens": tokens,
                    "chars": len(md_text),
                    "used_ocr": used_ocr
                })
            except Exception as e:
                failed_files.append((uploaded_file.name, str(e)))
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

    for fname, err in failed_files:
        st.error(f"Gagal mengonversi **{fname}**: {err}")

    if converted_results:
        total_files = len(converted_results)
        total_tokens = sum(item["tokens"] for item in converted_results)
        total_chars = sum(item["chars"] for item in converted_results)

        st.divider()
        col1, col2, col3 = st.columns(3)
        col1.metric("File Berhasil Dikonversi", f"{total_files} file")
        col2.metric("Total Estimasi Token", f"{total_tokens:,} token")
        col3.metric("Total Karakter", f"{total_chars:,} karakter")

        st.subheader("📦 Unduh Hasil Batch")
        dl_col1, dl_col2 = st.columns(2)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for item in converted_results:
                zf.writestr(item["md_filename"], item["content"])
        zip_buffer.seek(0)

        with dl_col1:
            st.download_button(
                label="⬇️ Download Semua (.ZIP)",
                data=zip_buffer,
                file_name="converted_markdown_files.zip",
                mime="application/zip",
                use_container_width=True
            )

        merged_md = "\n\n---\n\n".join(
            f"# Sumber File: {item['original_name']}\n\n{item['content']}"
            for item in converted_results
        )
        with dl_col2:
            st.download_button(
                label="📑 Gabungkan Semua ke 1 File (.MD)",
                data=merged_md.encode("utf-8"),
                file_name="merged_context.md",
                mime="text/markdown",
                use_container_width=True
            )

        st.subheader("🔍 Preview & Unduh Satuan")
        for idx, item in enumerate(converted_results):
            ocr_badge = " `[OCR]`" if item["used_ocr"] else ""
            with st.expander(
                f"📄 {item['md_filename']}{ocr_badge}  —  **{item['tokens']:,} token** ({item['chars']:,} karakter)",
                expanded=(total_files == 1)
            ):
                st.download_button(
                    label=f"⬇️ Unduh {item['md_filename']}",
                    data=item["content"].encode("utf-8"),
                    file_name=item["md_filename"],
                    mime="text/markdown",
                    key=f"dl_btn_{idx}"
                )
                st.code(item["content"], language="markdown")