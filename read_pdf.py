import pypdf
try:
    reader = pypdf.PdfReader('safeland_redesign_plan.pdf')
    text = '\n'.join([page.extract_text() for page in reader.pages])
    print(text)
except Exception as e:
    print(f"Error: {e}")
