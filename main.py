from markdown_coverter.doc_processor import DocProcessor
import glob
import os

processor = DocProcessor()

def create_instance(folder_input, folder_output):
    os.makedirs(folder_output, exist_ok=True)
    list_files_markdown = glob.glob(folder_input+"/*.pdf")
    for idx, file in enumerate(list_files_markdown):
        print("{} Start process : {}".format(idx, file))
        name_file = os.path.basename(file).replace(".pdf", "")
        path_save = folder_output + "/" + name_file + '.md'
        result = processor.convert_pdf_to_md(file)
        if result:
            with open(path_save, "w", encoding="utf-8") as f:
                f.write(result)
            print("Successfully saved file : {}".format(path_save))
        else :
            print("Error convert")

if __name__ == "__main__":
    folder_call = "data_test"
    folder_save = "save_results"
    create_instance(folder_call, folder_save)
