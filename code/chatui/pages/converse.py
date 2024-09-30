

import gradio as gr

from chatui.utils import database
from chatui.utils import localLlm
import os
import shutil

from chatui.utils import actions

TITLE = "Teaching Assistant Chatbot"
OUTPUT_TOKENS = 250
MAX_DOCS = 5

TITLE = "Teaching Assistant Chatbot"
current_file_path = os.path.dirname(__file__)
root = os.path.join(current_file_path, "../../../")
docs_path = os.path.join(root, "files", "docs")
truth_path = os.path.join(root, "files", "truth")
temp_path = os.path.join(root, "files", "temp")
#models_path = os.path.join(root, "models/models--microsoft--Phi-3-mini-4k-instruct")
models_path = os.path.join(root, "models")



css = """
    .preview {height: 55vh !important; overflow-y: scroll !important};
    .email-result {height: 30vh !important; overflow: scroll !important;};
    .feedback {height: 320px !important; overflow: scroll !important; max-height: 320px !important};
    .feedback-child {height: 100% !important};
    .half-screen {height: 40vh !important; overflow-y: scroll !important};
    .svelte-1kzox3m {height: 320px !important; overflow-y: scroll !important};
    .radio-group {height: 200px !important; max-height: 200px !important; overflow-y: scroll !important};
"""

def build_page() -> gr.Blocks:

    chatLLM = localLlm.Phi3LLM(cache_dir=models_path)
    requirements_nim = gr.State("mistralai/mistral-7b-instruct-v0.2")
    feedback_nim = gr.State("mistralai/mistral-7b-instruct-v0.2")
    summary_nim = gr.State("mistralai/mistral-7b-instruct-v0.2")
    
    with gr.Blocks(title=TITLE, fill_height=True, css=css) as page:
        gr.Markdown(f"# {TITLE}")

        
        with gr.Row(equal_height=False):

            ### PREVIEW COLUMN ###
            with gr.Column(scale=15, min_width=250):
                preview_window = gr.HighlightedText(
                    label="Document Preview",
                    interactive=False,
                    scale=10,
                    elem_classes=["preview"]
                )

                with gr.Tabs(selected=0, elem_classes=["feedback"]) as feedback_tabs:
                    with gr.TabItem("Feedback", elem_classes=["feedback"]):
                        feedback_window = gr.Textbox(
                            interactive=True,
                            label="Feedback & Comments",
                            elem_classes=["feedback"]
                        )
                            
                    with gr.TabItem("Generate", elem_classes=["feedback-child"]):
                        feedback_text = gr.Textbox(
                            interactive=True,
                            label="Generated Feedback Email",
                            elem_classes=["feedback-child"]
                        )
                        generate = gr.Button(
                            value="Generate Feedback",
                        )

            ### ACTIONS COLUMN ###
            with gr.Column(scale=20, min_width=350) as settings_column:
                with gr.Tabs(selected=0) as jobs:

                    ### UPLOAD DOCUMENTS TAB ###
                    with gr.TabItem("Upload"):
                        gr.Markdown("## Upload Documents Here")
                        ### Assignments row
                        with gr.Row():
                            # Assignments file upload
                            with gr.Column():
                                docs_file = gr.File(
                                    interactive=True,
                                    label="Upload students' documents", 
                                    file_types=[".pdf", ".docx", ".doc", ".txt"], 
                                    file_count="multiple",
                                    scale=1,
                                    height="32vh"
                                )
                                with gr.Row():
                                    docs_upload_button = gr.Button(
                                        value="Upload",
                                        scale=1
                                    )
                                    docs_clear_button = gr.ClearButton(
                                        [docs_file], value="Clear", scale=1
                                    )

                        ### Assignments file explorer
                            with gr.Column():
                                upload_assignments_explorer = gr.FileExplorer(
                                    interactive=True,
                                    root_dir=docs_path,
                                    label="Assignment Files",
                                    file_count='multiple',
                                    scale=1,
                                    height="32vh",
                                    ignore_glob="*.gitkeep"
                                )
                                upload_docs_delete_button = gr.Button(
                                    value="Delete selected files",
                                )

                        ### Requirements row
                        with gr.Row():
                            with gr.Column():
                                upload_requirements_file = gr.File(
                                    interactive=True,
                                    label="Upload requirements documents",
                                    file_types=[".pdf", ".docx", ".doc", ".txt"],
                                    file_count="multiple",
                                    scale=1,
                                    height="32vh"
                                )
                                with gr.Row():
                                    upload_requirements_button = gr.Button(
                                        value="Upload",
                                        scale=1
                                    )
                                    upload_clear_requirements_button = gr.ClearButton(
                                        [docs_file], value="Clear", scale=1
                                    )
                            with gr.Column():
                                upload_requirements_explorer = gr.FileExplorer(
                                    interactive=True,
                                    root_dir=truth_path,
                                    label="Requirements Files",
                                    file_count='multiple',
                                    height="32vh",
                                    ignore_glob="*.gitkeep"
                                )
                                upload_requirements_delete_button = gr.Button(
                                    value="Delete selected files",
                                )

                    with gr.TabItem("Criteria"):
                        gr.Markdown("## Set requirements here")
                        with gr.Tabs(selected=0) as method_tab:

                            # Auto handle criterias tab
                            with gr.TabItem("Auto"):
                                auto_criterias_group = gr.CheckboxGroup(
                                    interactive=True,
                                    label="No criterias found. Please upload the relevant documents",
                                    choices=[]
                                )
                                auto_find_criteria_button = gr.Button(
                                    value="Start finding criteria (Make sure you have uploaded the relevant documents)"
                                )
                                auto_delete_criteria_button = gr.Button(
                                    value="Delete the selected criterias"
                                )
                                truth_file = gr.File(
                                    interactive=True,
                                    label="Evalutation criteria documents",
                                    file_types=[".pdf", ".docx", ".doc", ".txt"],
                                    file_count="multiple"
                                )

                            # Manually input criterias tab
                            with gr.TabItem("Manual"):
                                
                                manual_criterias_group = gr.CheckboxGroup(
                                    label="Choose the criterias you want to assess",
                                    choices=[]
                                )
                                manual_delete_criteria_button = gr.Button(
                                    value="Delete selected criterias"
                                )
                                manual_add_criteria_textbox = gr.Textbox(
                                    interactive=True,
                                    label="Type in a criteria and press Enter",
                                    placeholder="Enter criteria"
                                )
                            
                    with gr.TabItem("Marking"):
                        gr.Markdown("## Assess students' assignments here")
                        
                        marking_output = gr.Textbox(
                            label="Marking output",
                            interactive=True,
                            scale=4,
                            show_copy_button=True,
                            max_lines=14
                        )

                        with gr.Row():
                            _ = gr.Markdown(
                                value= "#### Criteria Source:")
                            criteria_method = gr.Radio(
                                choices=["Auto", "Manual"], 
                                interactive=True,
                                value="Auto",
                                scale=4,
                                show_label=False,
                                container=False
                            )
                            marking_button = gr.Button(
                                value="Start Assessment",
                                scale =2,
                            )
                        docs_file_explorer = gr.FileExplorer(
                            root_dir=docs_path,
                            label="Assignment Files",
                            file_count='single',
                            scale=2,
                            height="30vh",
                            ignore_glob="*.gitkeep"
                        )
                        with gr.Row():
                            docs_preview_button = gr.Button(
                                value="Preview selected file",
                            )
                            docs_delete_button = gr.Button(
                                value="Delete selected files",
                            )
                        
                    with gr.TabItem("Summary"):
                        gr.Markdown("## Summary assignment here (It might take a while)")
                        with gr.Column():
                            assignment_summary = gr.Textbox(
                                label="Summary",
                                interactive=False,
                            )

                            assignment_summary_button = gr.Button(
                                value="Summarize"
                            )

                    with gr.TabItem("Email"):
                        gr.Markdown("## Resolve student email here")
                        with gr.Tabs(selected=0):
                            with gr.TabItem("Manually", elem_classes=["radio-group"]):
                                manual_email_textbox = gr.Textbox(
                                    label="Email content",
                                    placeholder="Enter email content",
                                    container=False,
                                    interactive=True,
                                    elem_classes=["email-result"],
                                    max_lines=12
                                )
                                

                                with gr.Row(equal_height=True):
                                    email_input_type = gr.Dropdown(
                                        label="Email input type",
                                        choices=["Single", "Multiple"],
                                        interactive=True,
                                        value="Single"
                                    )
                                    find_related_files_button = gr.Button(
                                        value="Find related files",
                                    )
                                    email_content_clear = gr.ClearButton(
                                        [manual_email_textbox], value="Clear email"
                                    )

                                with gr.Row(elem_classes=["radio-group"]):
                                    with gr.Column():
                                        _ = gr.Markdown(
                                            label="Result",
                                            value="Email content are displayed here",
                                            height="30vh"
                                        )
                                        manual_email_result_markdown= gr.Markdown(
                                            label="Result",
                                        )
                                    with gr.Group(elem_classes=["radio-group"]):
                                        manual_email_related_files_radio = gr.Radio(
                                            label="Related files",
                                            choices=[
                                                "Example longngnggnng choice to seee how it wraps",
                                                "Example choice",
                                                "Example choice alsjvasdf;j;a",
                                                "Example choice dajfajd",
                                                "Example choice",
                                                "Example choice",
                                                "Example choice",
                                                "Example choice",
                                                "Example choice",
                                                "Example choice",
                                                "Example choice",
                                                "Example choice",
                                                "Example choice",
                                                "Example choice",
                                                "Example choice",
                                            ],
                                            elem_classes=["radio-group"],
                                        )
                            with gr.TabItem("Via API"):
                                api_email_markdown = gr.Markdown(
                                    label="Email content",
                                    value="Email content are displayed here"
                                )
                    
                    with gr.TabItem("LLM"):
                        gr.Markdown ("## LLM Settings")

                        with gr.Column():
                            extract_requirements_dropdown = gr.Dropdown(
                                label="Extract Requirements LLM",
                                choices=["Local", "NVIDIA-hosted NIM"],
                            )
                            feedback_dropdown = gr.Dropdown(
                                label="Feedback LLM",
                                choices=["Local", "NVIDIA-hosted NIM"],
                            )
                            summary_dropdown = gr.Dropdown(
                                label="Summary LLM",
                                choices=["Local", "NVIDIA-hosted NIM"],
                            )
                            email_dropdown = gr.Dropdown(
                                label="Email LLM",
                                choices=["Local", "NVIDIA-hosted NIM"],
                            )

                    with gr.TabItem("Prompt"):
                        gr.Markdown("## Prompt customization")
                        with gr.Tabs():
                            with gr.TabItem("Extract Requirements Prompt"):
                                extract_requirements_textbox = gr.Textbox(
                                    label="Extract Requirements Prompt",
                                    interactive=True,
                                    
                                )
                            with gr.TabItem("Feedback"):
                                feedback_textbox = gr.Textbox(
                                    label="Feedback Prompt",
                                    interactive=True,
                                )
                            with gr.TabItem("Summary"):
                                summary_textbox = gr.Textbox(
                                    label="Summary Prompt",
                                    interactive=True,
                                )
                            with gr.TabItem("Email"):
                                email_textbox = gr.Textbox(
                                    label="Email Prompt",
                                    interactive=True,

                                )

        # Assignment files
        def upload_docs(files):
            if files:
                for file in files:
                    shutil.move(file.name, docs_path)
            return gr.FileExplorer(root_dir=temp_path,
                ignore_glob="*.gitkeep"), 
            gr.FileExplorer(root_dir=temp_path,
                ignore_glob="*.gitkeep"), None

        def delete_docs(files):
            if files:
                if (type(files) == list):
                    for file in files:
                        os.remove(file)  
                else:
                    os.remove(files)                  
                return gr.FileExplorer(root_dir=temp_path,
                                    ignore_glob="*.gitkeep"), gr.FileExplorer(root_dir=temp_path,
                                    ignore_glob="*.gitkeep")
            return docs_path, docs_path
        
        # Workaround for gr.FileExplorer not updating after file upload
        def delete_docs2(files, files2):
            return gr.FileExplorer(root_dir=docs_path,
                                    ignore_glob="*.gitkeep"), gr.FileExplorer(root_dir=docs_path,
                                    ignore_glob="*.gitkeep")
        
        docs_upload_button.click(upload_docs, inputs=[docs_file], outputs=[docs_file_explorer, upload_assignments_explorer, docs_file]).then(delete_docs2, inputs=[docs_file_explorer, upload_assignments_explorer], outputs=[docs_file_explorer, upload_assignments_explorer])
        docs_delete_button.click(delete_docs, inputs=[docs_file_explorer], outputs=[docs_file_explorer, upload_assignments_explorer]).then(delete_docs2, inputs=[docs_file_explorer, upload_assignments_explorer], outputs=[docs_file_explorer, upload_assignments_explorer])
        upload_docs_delete_button.click(delete_docs, inputs=[upload_assignments_explorer], outputs=[docs_file_explorer, upload_assignments_explorer]).then(delete_docs2, inputs=[docs_file_explorer, upload_assignments_explorer], outputs=[docs_file_explorer, upload_assignments_explorer])

        ### CRITERIA TAB EVENTS
        # Upload truth files
        def upload_truth(files):
            if files:
                database.upload_files(files)
                for file in files:
                    shutil.move(file.name, truth_path)
            return None, gr.FileExplorer(root_dir=truth_path, interactive=True,
                                    ignore_glob="*.gitkeep")
        
        def clear_truth(files):
            database.clear()
            if (files):
                for file in files:
                    os.remove(file)

            current_files = os.listdir(truth_path)
            if len(current_files) != 0:
                database.upload_files(current_files)
            return None

        upload_requirements_button.click(upload_truth, inputs=[upload_requirements_file], outputs=[upload_requirements_file, upload_requirements_explorer])
        upload_requirements_delete_button.click(clear_truth, inputs=[truth_file], outputs=[truth_file])

        # Auto infer criteria
        def auto_infer_criteria():
            documents = actions.retrieve_requirements()
            criterias = actions.extract_requirements(documents, chatLLM)

            if (type(criterias) == list):
                if (len(criterias) == 0):
                    label= "No criterias found. Please upload the relevant documents."
                else: 
                    label = "Choose the criterias to get feedback on!"
                return gr.CheckboxGroup(label=label, choices=criterias, interactive=True)
        
        def auto_delete_criteria(values):
            choices = auto_criterias_group.choices
            if values:
                for value in values:
                    choices.remove(value)

            if (len(choices) == 0):
                label= "No criterias found. Please upload the relevant documents."
            else: 
                label = "Choose the criterias to get feedback on!"
            return gr.CheckboxGroup(
                label=label,
                choices=choices,
                interactive=True
            )

        # Manually criterias tab events handling
        def manually_add_criteria(criteria):
            choices = manual_criterias_group.choices
            value = manual_criterias_group.value
            if criteria:
                choices.append(criteria)
            return "", gr.CheckboxGroup(
                label="Choose the criterias to get feedback on",
                choices=choices,
                value=value,
                interactive=True
            )
        
        def manual_delete_criteria(values):
            choices = manual_criterias_group.choices
            if values:
                for value in values:
                    choices.remove(value)
            return gr.CheckboxGroup(
                label="Choose the criterias to get feedback on",
                choices=choices,
                interactive=True
            )
            
        auto_find_criteria_button.click(auto_infer_criteria, outputs=[auto_criterias_group])
        auto_delete_criteria_button.click(auto_delete_criteria, inputs=[auto_criterias_group], outputs=[auto_criterias_group])
        manual_add_criteria_textbox.submit(manually_add_criteria, inputs=[manual_add_criteria_textbox], outputs=[manual_add_criteria_textbox,manual_criterias_group])
        manual_delete_criteria_button.click(manual_delete_criteria, inputs=[manual_criterias_group], outputs=[manual_criterias_group])

        ### SUMMARY TAB EVENTS
        def summarize_assignment(file_path):
            documents = actions.get_doc_splits(file_path)
            summary = actions.summarize_documents(documents, chatLLM)
            return summary
        
        assignment_summary_button.click(summarize_assignment, inputs=[docs_file_explorer], outputs=[assignment_summary])

        ### MARKING TAB EVENTS
        def assess_assignment(method, auto_criteria, manual_criteria, chosen_file):
            if method == "Auto":
                criterias = auto_criteria
            else:
                criterias = manual_criteria

            criteria = ""
            for i in range(len(criterias)):
                criteria += str(i+1) + ". " + criterias[i] + "\n"
            result = actions.get_feedback(criteria, chosen_file, chatLLM)
            return result

        def preview_assignment(file_path, current_text):
            if type(file_path) == str:
                text = actions.get_text_from_file(file_path)
                return [(text, None)]
            else:
                return [(current_text, None)]

        marking_button.click(assess_assignment, inputs=[criteria_method, auto_criterias_group, manual_criterias_group, docs_file_explorer], outputs=[marking_output])
        docs_preview_button.click(preview_assignment, inputs=[docs_file_explorer, preview_window], outputs=[preview_window])

        ### EMAIL TAB EVENTS
        def infer_email(text):
            chain = actions.infer_email_chain(chatLLM)
            response = chain.invoke({"prompt": text})
            return (response)
        #email_infer.click(infer_email, inputs=[manual_email_textbox], outputs=[manual_email_result_textbox])

        def find_related_files(email):
            assignment_files = os.listdir(docs_path)
            truth_files = os.listdir(truth_path)
            f = assignment_files + truth_files
            markdown, related_files = actions.find_related_files_from_email(email, f, chatLLM)
            print(related_files)
            return markdown, gr.Radio(
                label="Related files",
                choices=related_files,
                interactive=True
            )
        
        def show_file_content(file_name):
            path = os.path.join(docs_path, file_name)
            if os.path.isfile(path):
                text = actions.get_text_from_file(path)
                return [(text, None)]

        find_related_files_button.click(find_related_files, inputs=[manual_email_textbox], outputs=[manual_email_result_markdown, manual_email_related_files_radio])
        manual_email_related_files_radio.input(show_file_content, inputs=[manual_email_related_files_radio], outputs=[preview_window])

    page.queue()
    return page