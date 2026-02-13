from langchain_community.document_loaders import Docx2txtLoader, UnstructuredWordDocumentLoader
from langchain_core.documents import Document
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter



class DocxProcessor:
    def __init__(self, chunk_size = 600, chunk_overlap = 80):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = chunk_size,
            chunk_overlap = chunk_overlap,
            separators=[" "],
            length_function = len
        )

    def __clean_text(self, text:str):
            """clean extracted text"""
            #Remove excessive white spaces
            text = " ".join(text.split())

            #fix common PDF extraction issues
            text = text.replace('fi', 'fi')
            text = text.replace('fl', 'fl')

            return text

    def process_docx(self, docxPath : str ) -> List[Document]:
            """Process Docx with smart chunking and metadata enhancement"""

            loader = Docx2txtLoader(docxPath)
            pages = loader.load()

            #processed chunks
            processed_chunks = []
            for page_num, page in enumerate(pages):
                # clean the text
                cleaned_text = self.__clean_text(page.page_content)

                #skip the empty pages
                if len(cleaned_text.strip()) < 50:
                    continue
                chunks = self.text_splitter.create_documents(
                                texts=[cleaned_text],
                                metadatas=[{
                                    **page.metadata,
                                    "page":page_num+1,
                                    "total_pages":len(pages),
                                    "chunk_method":"smart_docx_processor",
                                    "char_count":len(cleaned_text)
                                }]
                            )
            processed_chunks.extend(chunks)
            return processed_chunks
        
if __name__ == '__main__':
    preprocessor = DocxProcessor()
    try:
        smart_chunks = preprocessor.process_docx("./data/sample.docx")
        print(f"processes into {len(smart_chunks)} smart chunks")

        if smart_chunks:
            print("\n smaple chunk metadata:")
            for key, value in smart_chunks[0].metadata.items():
                print(f"{key}: {value}")
    except Exception as e:
        print(f"processiing Error: {e}")


