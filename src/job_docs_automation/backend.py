"""Contains the backend logic for generating a motivation letter using OpenAI API."""

import os
import re
from typing import Dict, Match

from openai import OpenAI
from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Pt

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# Define function to read content from a file
def read_file(file_path: str) -> str:
    """
    Reads the content of a file and returns it as a string.

    Parameters
    ----------
    file_path : str
        The path to the file to be read.

    Returns
    -------
    str
        The content of the file as a string.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# Define function to replace placeholders in prompts
def replace_placeholders(text: str, replacements: Dict[str, str]) -> str:
    """
    Replaces placeholders in the text with corresponding values
    from the replacements dictionary.

    Parameters
    ----------
    text : str
        The input text containing placeholders in the format <key>.
    replacements : Dict[str, str]
        A dictionary mapping keys to their replacement values.

    Returns
    -------
    str
        The text with placeholders replaced.
    """

    def replace_match(match: Match[str]) -> str:
        """
        Replace a single placeholder match with the corresponding value
        from the replacements dictionary.

        Parameters
        ----------
        match : Match[str]
            A regex match object containing the placeholder key.

        Returns
        -------
        str
            The replacement value for the placeholder,
            or the original placeholder if no match is found.
        """
        key = match.group(1)
        assert (
            key in replacements
        ), f"KeyError: Replacement key '{key}' not found in replacements dictionary."
        return replacements[key]

    return re.sub(r"<(\w+)>", replace_match, text)


# Define function to generate text using OpenAI API
def generate_text(
    api_key: str,
    prompt: str,
    replacements: Dict[str, str],
    max_loops: int = 5,
    initial_prompt: str = "",
) -> str:
    """
    Generates text using OpenAI API with placeholders dynamically replaced at runtime.

    Parameters
    ----------
    api_key : str
        The OpenAI API key.
    prompt : str
        The prompt to be processed and sent to the OpenAI API.
    replacements : Dict[str, str]
        A dictionary containing replacement values for placeholders in the prompt.
    max_loops : int, optional
        The maximum number of loops to replace placeholders, by default 5.

    Returns
    -------
    str
        The generated text from the OpenAI API.
    """
    processed_prompt = prompt
    loop_count = 0

    while re.search(r"<(\w+)>", processed_prompt):
        processed_prompt = replace_placeholders(processed_prompt, replacements)
        loop_count += 1

        if loop_count >= max_loops:
            user_input = (
                input(
                    "The prompt still contains placeholders. Do you want to continue replacing? (yes/no): "
                )
                .strip()
                .lower()
            )
            if user_input != "yes":
                break

    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
    )
    messages = []
    if initial_prompt:
        messages.append(
            {"role": "developer", "content": [{"type": "text", "text": initial_prompt}]}
        )
    messages.append({"role": "user", "content": [{"type": "text", "text": processed_prompt}]})
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4o",
    )

    response_text = (
        response.choices[0].message.content
        if response.choices[0].message.content is not None
        else ""
    )

    return response_text


# Define function to save the letter as a formatted .docx file
def save_to_docx(content: str, output_file: str) -> None:
    """
    Saves the content to a .docx file with Garamond font and size 11.

    Parameters
    ----------
    content : str
        The content to be saved to the document.
    output_file : str
        The path to the output .docx file.
    """
    doc = Document()

    # Set the default style to Garamond, size 11
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Garamond"
    font.size = Pt(11)

    # Add content to the document
    for paragraph in content.split("\n\n"):
        p = doc.add_paragraph(paragraph)
        p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT

    # Save the document
    doc.save(os.path.join("outputs", output_file))


# Main function
def main() -> None:
    """
    Main function to generate a motivation letter based on inputs and save it to a .docx file.
    """
    # Read input and prompt names from files
    input_names = read_file(os.path.join("inputs", "inputs.txt")).strip().split("\n")
    prompt_names = read_file(os.path.join("inputs", "prompts.txt")).strip().split("\n")
    initial_prompt = read_file(os.path.join("inputs", "initial_prompt.txt"))

    # Load inputs dynamically
    inputs = {name: read_file(os.path.join("inputs", f"{name}.txt")) for name in input_names}

    # Prepare replacements dictionary
    replacements = {key: value for key, value in inputs.items()}

    # Load prompts dynamically
    prompts = [(name, read_file(os.path.join("inputs", f"{name}.txt"))) for name in prompt_names]

    # Sequentially generate outputs and update replacements
    outputs = {}
    for prompt_name, prompt_template in prompts:
        outputs[prompt_name] = generate_text(
            api_key="your_openai_api_key",
            prompt=prompt_template,
            replacements=replacements,
            max_loops=5,
            initial_prompt=initial_prompt,
        )
        replacements[prompt_name] = outputs[
            prompt_name
        ]  # Update replacements with the generated output
        print(f"Input processed for {prompt_name}:\n")
        print(f"{prompt_template}\n")
        print(f"Generated output for {prompt_name}:\n")
        print(f"{outputs[prompt_name]}\n\n")
        pass

    # Save to .docx
    output_file = "motivation_letter.docx"
    save_to_docx(outputs["write_motivation_letter"], output_file)

    print(f"Motivation letter saved to {output_file}")


if __name__ == "__main__":

    main()
