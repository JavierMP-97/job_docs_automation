"""Contains the backend logic for generating a motivation letter using OpenAI API."""

import os
import re
from typing import Dict, List, Match, Optional, Tuple

from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Pt
from openai import OpenAI, api_key

class Prompt:
    name: str
    prompt: str
    prompt_input: str

    def __init__(self, name: str, prompt: str, prompt_input: str):
        self.name = name
        self.prompt = prompt
        self.prompt_input = prompt_input

    def replace_input(self, replacements: Dict[str, str], max_iterations: int) -> Optional[str]:
        """
        Replace placeholders in the input with the corresponding values from the replacements dictionary.

        Parameters
        ----------
        replacements : Dict[str, str]
            A dictionary mapping keys to their replacement values.
        max_iterations : int
            The maximum number of iterations to replace placeholders.

        Returns
        -------
        Optional[str]
            The input with placeholders replaced. If the process exceeds the maximum number of iterations, returns None.
        """
        processed_input = self.prompt_input
        loop_count = 0

        while re.search(r"<(\w+)>", processed_input):
            processed_input = replace_placeholders(processed_input, replacements)
            loop_count += 1

            if loop_count >= max_iterations:
                return None

        return processed_input


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


def read_files(
    input_filenames: str,
    prompt_filenames: str,
) -> Tuple[Dict[str, str], List[Prompt]]:
    """
    Reads the input and prompt files and returns their content.

    Parameters
    ----------
    input_filenames : str
        The path to the file containing the input filenames.
    prompt_filenames : str
        The path to the file containing the prompt filenames.

    Returns
    -------
    Tuple[Dict[str, str], List[Prompt]]
        A tuple containing a dictionary of inputs, and a list of prompts.
    """
    # Read input and prompt names from files
    input_names = read_file(os.path.join("inputs", input_filenames)).strip().split("\n")
    prompt_names = read_file(os.path.join("inputs", prompt_filenames)).strip().split("\n")
    # Load inputs dynamically
    inputs = {name: read_file(os.path.join("inputs", f"{name}.txt")) for name in input_names}

    # Load prompts dynamically
    prompts = [
        Prompt(
            name,
            read_file(os.path.join("prompts", name, "prompt.txt")),
            read_file(os.path.join("prompts", name, "input.txt")),
        )
        for name in prompt_names
    ]

    return inputs, prompts


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


def execute_step(step: int, prompts: List[Prompt], replacements: Dict[str, str]) -> Optional[str]:
    """
    Executes a step in the process of generating a motivation letter.

    Parameters
    ----------
    step : int
        The step
    prompts : List[Prompt]
        A list of prompts to be processed sequentially.
    replacements : Dict[str, str]
        A dictionary containing replacement values for placeholders in the prompts.

    Returns
    -------
    Optional[str]
        The output text for the step, or None if the call fails.
    """
    if step < len(prompts):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            return None
        output = generate_text(
            api_key=api_key,
            prompt=prompts[step],
            replacements=replacements,
            max_loops=5,
        )
        replacements[prompts[step].name] = output
        return output
    return None


# Define function to generate text using OpenAI API
def generate_text(
    api_key: str,
    prompt: Prompt,
    replacements: Dict[str, str],
    max_loops: int = 5,
) -> str:
    """
    Generates text using OpenAI API with placeholders dynamically replaced at runtime.

    Parameters
    ----------
    api_key : str
        The OpenAI API key.
    prompt : Prompt
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

    client = OpenAI(
        api_key=api_key,  # This is the default and can be omitted
    )
    messages = []
    if prompt:
        messages.append({"role": "developer", "content": [{"type": "text", "text": prompt.prompt}]})
    messages.append(
        {
            "role": "user",
            "content": [{"type": "text", "text": prompt.replace_input(replacements, max_loops)}],
        }
    )
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

    initial_prompt, inputs, prompts = read_files()

    # Prepare replacements dictionary
    replacements = {key: value for key, value in inputs.items()}

    # Sequentially generate outputs and update replacements
    for i, prompt in enumerate(prompts):
        output = execute_step(
            step=i, initial_prompt=initial_prompt, prompts=prompts, replacements=replacements
        )
        print(f"Input processed for {prompt[0]}:\n")
        print(f"{prompt[1]}\n")
        print(f"Generated output for {prompt[0]}:\n")
        print(f"{output}\n\n")
        pass

    # Save to .docx
    output_file = "motivation_letter.docx"
    save_to_docx(replacements["write_motivation_letter"], output_file)

    print(f"Motivation letter saved to {output_file}")


if __name__ == "__main__":

    main()
