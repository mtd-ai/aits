

import gradio as gr

from chatui.utils import database
from chatui.utils import localLlm
from langchain_nvidia_ai_endpoints import ChatNVIDIA
import os
import shutil

from chatui.utils import actions
import os

TITLE = "AI Academic Feedback Assistant"
OUTPUT_TOKENS = 250
MAX_DOCS = 5

current_file_path = os.path.dirname(__file__)
root = os.path.join(current_file_path, "../../../")
docs_path = os.path.join(root, "files", "docs")
truth_path = os.path.join(root, "files", "truth")
temp_path = os.path.join(root, "files", "temp")
feedback_path = os.path.join(root, "files", "feedback")
#models_path = os.path.join(root, "models")

models_path = "/"

css = """
    .preview {height: 45vh !important; overflow-y: scroll !important};
    .email-result {height: 30vh !important; overflow: scroll !important;};
    .feedback {height: 320px !important; overflow: scroll !important; max-height: 320px !important};
    .feedback-child {height: 35vh !important};
    .half-screen {height: 320px !important; overflow-y: scroll !important};
    .radio-group {height: 200px !important; max-height: 200px !important; overflow-y: scroll !important};
"""

def build_page() -> gr.Blocks:

    chatLLM = localLlm.Phi3LLM(cache_dir=models_path)
    nim_choices = ["mistralai/mistral-7b-instruct-v0.3", "meta/llama3-8b-instruct", "nvidia/nemotron-mini-4b-instruct"]
    
    with gr.Blocks(title=TITLE, fill_height=True, css=css) as page:

        with gr.Row():
            gr.Markdown(f"# {TITLE}")
            gr.Image(
                height=64,
                width=64,
                value=os.path.join(root, "static", "logo.png"), 
                scale=0.1, 
                container=False,
                show_download_button=False,
                show_fullscreen_button=False,
            )
        auto_criterias_choices = gr.State([])
        manual_criterias_choices = gr.State([])

        
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
                            label="Feedback",
                            elem_classes=["feedback"]
                        )
                            
                    with gr.TabItem("Generate", elem_classes=["feedback-child"]):
                        feedback_text = gr.Textbox(
                            interactive=True,
                            label="Auto Generate Feedback Email",
                            elem_classes=["feedback-child"]
                        )
                        generate_email_button = gr.Button(
                            value="Start Generate Feedback",
                        )
                    with gr.TabItem("Comment"):
                        comment_textbox = gr.Textbox(
                            interactive=True,
                            label="Write your comment",
                        )
                        comment_save_button = gr.Button(
                            value="Save comment",
                        )

            ### ACTIONS COLUMN ###
            with gr.Column(scale=20, min_width=350) as settings_column:
                with gr.Tabs(selected=0) as jobs:

                    ### UPLOAD DOCUMENTS TAB ###
                    with gr.TabItem("Upload"):
                        
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
                                    _ = gr.ClearButton(
                                        [upload_requirements_file], 
                                        value="Clear", 
                                        scale=1
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

                    with gr.TabItem("Requirements"):
                        gr.Markdown("## Manage your requirements")
                            
                        with gr.Tabs(selected=0) as method_tab:

                            # Auto handle criterias tab
                            with gr.TabItem("Auto"):
                                auto_criterias_group = gr.CheckboxGroup(
                                    interactive=True,
                                    label="No requirements found. Please upload the relevant documents",
                                    choices=[],
                                    value=[]
                                )
                                auto_find_criteria_button = gr.Button(
                                    value="Start finding requirements (Make sure you have uploaded the relevant documents)"
                                )
                                auto_delete_criteria_button = gr.Button(
                                    value="Delete the selected requirements"
                                )
                                auto_criteria_explorer = gr.FileExplorer(
                                    interactive=False,
                                    label="Uploaded documents",
                                    root_dir=truth_path,
                                    ignore_glob="*.gitkeep",
                                    value=[]
                                )

                            # Manually input criterias tab
                            with gr.TabItem("Manual"):
                                
                                manual_criterias_group = gr.CheckboxGroup(
                                    label="Choose the requirements you want to assess",
                                    choices=[],
                                    value=[],
                                    elem_classes=["half-screen"],
                                )
                                manual_delete_criteria_button = gr.Button(
                                    value="Delete selected requirements"
                                )
                                manual_add_criteria_textbox = gr.Textbox(
                                    interactive=True,
                                    label="Type in a requirement and press Enter",
                                    placeholder="Enter criteria"
                                )
                            
                    with gr.TabItem("Feedback"):
                        gr.Markdown("## Assess students' assignments here")
                        
                        marking_output = gr.Textbox(
                            label="Feedback output",
                            interactive=True,
                            scale=4,
                            show_copy_button=True,
                            max_lines=14
                        )

                        with gr.Row():
                            _ = gr.Markdown(
                                value= "#### Requirement Source:")
                            criteria_method = gr.Radio(
                                choices=["Auto", "Manual"], 
                                interactive=True,
                                value="Auto",
                                scale=4,
                                show_label=False,
                                container=False
                            )
                            marking_button = gr.Button(
                                value="Generate Feedback",
                                scale =2,
                            )

                        with gr.Row():
                            docs_file_explorer = gr.FileExplorer(
                                root_dir=docs_path,
                                label="Please choose a file to feedback",
                                file_count='multiple',
                                scale=2,
                                height="30vh",
                                ignore_glob="*.gitkeep"
                            )
                            feedback_explorer = gr.FileExplorer(
                                interactive=True,
                                root_dir=feedback_path,
                                label="Feedback Files",
                                file_count='multiple',
                                scale=2,
                                height="30vh",
                                ignore_glob="*.gitkeep"
                            )
                        with gr.Row():
                            docs_preview_button = gr.Button(
                                value="Preview selected document file",
                            )
                            feedback_preview_button = gr.Button(
                                value="Preview selected feedback file",
                            )
                        with gr.Row():
                            feedback_all_button = gr.Button(
                                value="Feedback all selected files",
                            )
                            feedback_delete_button = gr.Button(
                                value="Delete selected feedback files",
                            )
                        
                        with gr.Row():
                            feedback_everything_button = gr.Button(
                                value="Feedback all files",
                            )
                            feedback_delete_everything_button = gr.Button(
                                value="Delete all feedback files",
                            )
                    with gr.TabItem("Summary"):
                        gr.Markdown("## Summary assignment here (It might take a while)")

                        summary_explorer = gr.FileExplorer(
                            interactive=True,
                            file_count='single',
                            root_dir=docs_path,
                            label="Choose a file to summarize",
                            ignore_glob="*.gitkeep",
                            height="30vh"
                        )
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
                        #with gr.Tabs(selected=0):
                            #with gr.TabItem("Manually", elem_classes=["radio-group"]):
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
                                        
                                    ],
                                    elem_classes=["radio-group"],
                                )
                            #with gr.TabItem("Via API"):
                               # api_email_markdown = gr.Markdown(
                                    #label="Email content",
                                    #value="Email content are displayed here"
                                #)
                    
                    with gr.TabItem("LLM"):
                        gr.Markdown ("## LLM Settings")

                        with gr.Column():
                            with gr.Row():
                                requirements_llm_dropdown = gr.Dropdown(
                                    label="Requirements LLM mode",
                                    choices=["Local", "NVIDIA-hosted NIM"],
                                    value="Local",
                                    interactive=True
                                )
                                requirements_nim_dropdown = gr.Dropdown(
                                    label="NIM model (Only for NVIDIA-hosted LLM)",
                                    choices=nim_choices,
                                    value="mistralai/mistral-7b-instruct-v0.3",
                                    interactive=True
                                )
                            with gr.Row():
                                feedback_llm_dropdown = gr.Dropdown(
                                    label="Feedback LLM mode",
                                    choices=["Local", "NVIDIA-hosted NIM"],
                                    value="Local",
                                    interactive=True
                                )
                                feedback_nim_dropdown = gr.Dropdown(
                                    label="NIM model (Only for NVIDIA-hosted LLM)",
                                    choices=nim_choices,
                                    value="mistralai/mistral-7b-instruct-v0.3",
                                    interactive=True
                                )
                            with gr.Row():
                                summary_llm_dropdown = gr.Dropdown(
                                    label="Summary LLM mode",
                                    choices=["Local", "NVIDIA-hosted NIM"],
                                    value="Local",
                                    interactive=True
                                )
                                summary_nim_dropdown = gr.Dropdown(
                                    label="NIM model (Only for NVIDIA-hosted LLM)",
                                    choices=nim_choices,
                                    value="mistralai/mistral-7b-instruct-v0.3",
                                    interactive=True
                                )
                            with gr.Row():
                                email_llm_dropdown = gr.Dropdown(
                                    label="Email LLM mode",
                                    choices=["Local", "NVIDIA-hosted NIM"],
                                    value="Local",
                                    interactive=True
                                )
                                email_nim_dropdown = gr.Dropdown(
                                    label="NIM model (Only for NVIDIA-hosted LLM)",
                                    choices=nim_choices,
                                    value="mistralai/mistral-7b-instruct-v0.3",
                                    interactive=True
                                )


        def get_llm(state, model):
            if state == "Local":
                return chatLLM
            else:
                return ChatNVIDIA(model=model)
            
        ### UPLOAD TAB EVENTS ###
        # Assignment files
        def upload_docs(files):
            if files:
                for file in files:
                    shutil.move(file.name, docs_path)
            return gr.FileExplorer(
                root_dir=temp_path,
                ignore_glob="*.gitkeep"
            ), gr.FileExplorer(
                root_dir=temp_path,
                ignore_glob="*.gitkeep"
            ), None

        def delete_docs(files):
            if files:
                for file in files:
                    os.remove(file)                   
            return gr.FileExplorer(
                root_dir=temp_path,
                ignore_glob="*.gitkeep"
            ), gr.FileExplorer(
                root_dir=temp_path,
                ignore_glob="*.gitkeep"
            )
        
        # Workaround for gr.FileExplorer not updating after file upload
        def delete_docs2(files, files2):
            return gr.FileExplorer(
                interactive=True,
                root_dir=docs_path,
                label="Please choose a file to feedback",
                file_count='multiple',
                scale=2,
                height="30vh",
                ignore_glob="*.gitkeep",
                value=[]
            ), gr.FileExplorer(
                interactive=True,
                root_dir=docs_path,
                label="Assignment Files",
                file_count='multiple',
                scale=1,
                height="32vh",
                ignore_glob="*.gitkeep",
                value=[]
            )
        
        docs_upload_button.click(upload_docs, inputs=[docs_file], outputs=[docs_file_explorer, upload_assignments_explorer, docs_file]).then(delete_docs2, inputs=[docs_file_explorer, upload_assignments_explorer], outputs=[docs_file_explorer, upload_assignments_explorer])
        upload_docs_delete_button.click(delete_docs, inputs=[upload_assignments_explorer], outputs=[docs_file_explorer, upload_assignments_explorer]).then(delete_docs2, inputs=[docs_file_explorer, upload_assignments_explorer], outputs=[docs_file_explorer, upload_assignments_explorer])

        # Upload truth files
        def upload_truth(files):
            current_files = [os.path.join(truth_path, file_name) for file_name in os.listdir(truth_path)]
            new_files = []
            if files:
                for file1 in files:
                    isnew = True
                    for file2 in current_files:
                        if os.path.samefile(file1, file2):
                            isnew = False
                    if isnew:
                        new_path = shutil.move(file1, truth_path)
                        new_files.append(new_path)
                database.upload_files(new_files)
            return None, gr.FileExplorer(
                                    interactive=True,
                                    root_dir=temp_path,
                                ), gr.FileExplorer(
                                    interactive=False,
                                    root_dir=temp_path,
                                )
        
        # Delete truth files
        def clear_truth(files):
            if (files):
                database.clear()
                old_files = [os.path.join(truth_path, file_name) for file_name in os.listdir(truth_path) if file_name != ".gitkeep"]
                for file1 in files:
                    for file2 in old_files:
                        print("file1: ", file1, "file2: ", file2)
                        if os.path.samefile(file1, file2):
                            os.remove(file2)
                            break

            current_files = [os.path.join(truth_path, file_name) for file_name in os.listdir(truth_path) if file_name != ".gitkeep"]
            if len(current_files) != 0:
                database.upload_files(current_files)
            return gr.FileExplorer(root_dir=temp_path, interactive=True), gr.FileExplorer(root_dir=temp_path, interactive=False)

        # Workaround for gr.FileExplorer not updating after file upload
        def reset_truth_explorer():
            return gr.FileExplorer(
                interactive=True,
                root_dir=truth_path,
                label="Requirements Files",
                file_count='multiple',
                height="32vh",
                ignore_glob="*.gitkeep",
                value=[]
            ), gr.FileExplorer(
                interactive=False,
                root_dir=truth_path,
                label="Uploaded Documents",
                height="32vh",
                ignore_glob="*.gitkeep",
                value=[]
            )
        
        upload_requirements_button.click(upload_truth, inputs=[upload_requirements_file], outputs=[upload_requirements_file, upload_requirements_explorer, auto_criteria_explorer]).then(reset_truth_explorer, inputs=[], outputs=[upload_requirements_explorer, auto_criteria_explorer])
        upload_requirements_delete_button.click(clear_truth, inputs=[upload_requirements_explorer], outputs=[upload_requirements_explorer, auto_criteria_explorer]).then(reset_truth_explorer, inputs=[], outputs=[upload_requirements_explorer, auto_criteria_explorer])


        ### CRITERIA TAB EVENTS ###
        # Auto infer criteria
        def auto_infer_criteria(mode, model):
            llm = get_llm(mode, model)
            documents = actions.retrieve_requirements()
            criterias = actions.extract_requirements(documents, llm)

            if (type(criterias) == list):
                if (len(criterias) == 0):
                    label= "No criterias found. Please upload the relevant documents."
                else: 
                    label = "Choose the criterias to get feedback on!"
                return gr.CheckboxGroup(label=label, choices=criterias, value=[],interactive=True), criterias, mode, model
        
        def auto_delete_criteria(values, choices):

            if values:
                for value in values:
                    print(value)
                    print(choices)
                    choices.remove(value)

            print(type(choices))

            if (len(choices) == 0):
                label= "No criterias found. Please upload the relevant documents."
            else: 
                label = "Choose the criterias to get feedback on!"
            return gr.CheckboxGroup(
                label=label,
                choices=choices,
                value=[],
                interactive=True
            ), choices

        # Manually criterias tab events handling
        def manually_add_criteria(criteria, values, choices):
            if criteria:
                choices.append(criteria)
            return "", gr.CheckboxGroup(
                label="Choose the criterias to get feedback on",
                choices=choices,
                value=values,
                interactive=True
            ), choices
        
        def manual_delete_criteria(values, choices):
            if values:
                for value in values:
                    choices.remove(value)
            return gr.CheckboxGroup(
                label="Choose the criterias to get feedback on",
                choices=choices,
                value=[],
                interactive=True
            ), choices
            
        auto_find_criteria_button.click(auto_infer_criteria, inputs=[requirements_llm_dropdown, requirements_nim_dropdown], outputs=[auto_criterias_group, auto_criterias_choices, requirements_llm_dropdown, requirements_nim_dropdown])
        auto_delete_criteria_button.click(auto_delete_criteria, inputs=[auto_criterias_group, auto_criterias_choices], outputs=[auto_criterias_group, auto_criterias_choices])
        manual_add_criteria_textbox.submit(manually_add_criteria, inputs=[manual_add_criteria_textbox, manual_criterias_group, manual_criterias_choices], outputs=[manual_add_criteria_textbox,manual_criterias_group, manual_criterias_choices])
        manual_delete_criteria_button.click(manual_delete_criteria, inputs=[manual_criterias_group, manual_criterias_choices], outputs=[manual_criterias_group, manual_criterias_choices])

        

        ### MARKING TAB EVENTS
        def assess_assignment(method, auto_criteria, manual_criteria, chosen_file, mode, model):
            if (not chosen_file) or len(chosen_file) == 0:
                return "", mode, model
            llm = get_llm(mode, model)
            if method == "Auto":
                criterias = auto_criteria
            else:
                criterias = manual_criteria

            criteria = ""
            for i in range(len(criterias)):
                criteria += str(i+1) + ") " + criterias[i] + "\n"
            
            result = actions.get_feedback(criteria, chosen_file[0], llm)
            return result, mode, model

        def preview_assignment(file_path, current_text):
            if type(file_path) == list and len(file_path) >0 and type(file_path[0]) == str:
                text = actions.get_text_from_file(file_path[0])
                return [(text, None)]
            else:
                return current_text

        def preview_feedback(file_path, current_text):
            print(file_path)
            all_assignments = os.listdir(docs_path)
            if type(file_path) == list and len(file_path) >0 and type(file_path[0]) == str:
                print("isfile")
                file = file_path[0]
                for f in all_assignments:
                    if f.startswith(file):
                        file = f
                        break
                file_name = os.path.basename(file).split('/')[-1].split('.')[0]
                assignment_path = None
                for f in all_assignments:
                    if f.startswith(file_name):
                        assignment_path = f
                        break
                assignment_path = os.path.join(docs_path, assignment_path)
                feedback_text = actions.get_text_from_file(file)
                assignment_text = ""
                if assignment_path:
                    assignment_text = actions.get_text_from_file(assignment_path)
                return gr.HighlightedText(
                    value=[(assignment_text, None)],
                    label="Document Preview",
                    interactive=False,
                    scale=10,
                    elem_classes=["preview"]
                ), gr.Textbox(
                    value=feedback_text,
                    label="Feedback",
                    interactive=True,
                    elem_classes=["feedback"]
                )
            return gr.HighlightedText(
                    value=current_text,
                    label="Document Preview",
                    interactive=False,
                    scale=10,
                    elem_classes=["preview"]
                ), ""
        
        def feedback_all_files(method, auto_criteria, manual_criteria, files, mode, model):
            llm = get_llm(mode, model)
            if method == "Auto":
                criterias = auto_criteria
            else:
                criterias = manual_criteria

            actions.create_all_feedback(criterias, files, llm)
            return gr.FileExplorer(root_dir=temp_path, interactive=False)

        def reset_feedback_explorer():
            return gr.FileExplorer(
                root_dir=feedback_path,
                interactive=True,
                label="Feedback Files",
                file_count='multiple',
                scale=2,
                height="30vh",
                ignore_glob="*.gitkeep",
                value=[]
            )
            
        def delete_feedback(files):
            if files:
                for file in files:
                    os.remove(file)
            return gr.FileExplorer(
                root_dir=temp_path,
            )

        marking_button.click(assess_assignment, inputs=[criteria_method, auto_criterias_group, manual_criterias_group, docs_file_explorer, feedback_llm_dropdown, feedback_nim_dropdown], outputs=[marking_output, feedback_llm_dropdown, feedback_nim_dropdown])
        docs_preview_button.click(preview_assignment, inputs=[docs_file_explorer, preview_window], outputs=[preview_window])
        feedback_all_button.click(feedback_all_files, inputs=[criteria_method, auto_criterias_group, manual_criterias_group, docs_file_explorer, feedback_llm_dropdown, feedback_nim_dropdown], outputs=[feedback_explorer]).then(reset_feedback_explorer, inputs=[], outputs=[feedback_explorer])
        feedback_preview_button.click(preview_feedback, inputs=[feedback_explorer, preview_window], outputs=[preview_window, feedback_window])
        feedback_delete_button.click(delete_feedback, inputs=[feedback_explorer], outputs=[feedback_explorer]).then(reset_feedback_explorer, inputs=[], outputs=[feedback_explorer]).then(reset_feedback_explorer, inputs=[], outputs=[feedback_explorer])

        ### SUMMARY TAB EVENTS
        def summarize_assignment(file_path, mode, model):
            llm = get_llm(mode, model)
            documents = actions.get_doc_splits(file_path)
            summary = actions.summarize_documents(documents, llm)
            return summary, mode, model
        
        assignment_summary_button.click(summarize_assignment, inputs=[summary_explorer, summary_llm_dropdown, summary_nim_dropdown], outputs=[assignment_summary, summary_llm_dropdown, summary_nim_dropdown])

        ### EMAIL TAB EVENTS
        def infer_email(text):
            chain = actions.infer_email_chain(chatLLM)
            response = chain.invoke({"prompt": text})
            return (response)
        #email_infer.click(infer_email, inputs=[manual_email_textbox], outputs=[manual_email_result_textbox])

        def find_related_files(email, mode, model):
            assignment_files = os.listdir(docs_path)
            truth_files = os.listdir(truth_path)
            f = assignment_files + truth_files
            llm = get_llm(mode, model)
            markdown, related_files = actions.find_related_files_from_email(email, f, llm)
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

        def generate_feedback_email(email, comments, mode, model):
            if not comments or len(comments) == 0:
                return ""
            if not email or len(email) == 0:
                return ""
            llm = get_llm(mode, model)


            response = actions.generate_response_email(email, comments, llm)
            return response


        find_related_files_button.click(find_related_files, inputs=[manual_email_textbox, email_llm_dropdown, email_nim_dropdown], outputs=[manual_email_result_markdown, manual_email_related_files_radio])
        manual_email_related_files_radio.input(show_file_content, inputs=[manual_email_related_files_radio], outputs=[preview_window])

        generate_email_button.click(generate_feedback_email, inputs=[manual_email_textbox, comment_textbox, email_llm_dropdown, email_nim_dropdown], outputs=[feedback_text])

    page.queue()
    return page