import os

def read_file_chunks(file_path, min_chars=3400, max_chars=3641):
    with open(file_path, 'r') as file:
        while True:
            text = file.read(max_chars)
            if not text:
                break

            if len(text) < min_chars:
                yield text
                break

            last_period = text.rfind('.')
            last_quote = text.rfind('"')
            last_space = max(last_period, last_quote)

            if last_space != -1 and last_space > min_chars:
                file.seek(file.tell() - (len(text) - last_space - 1))
                text = text[:last_space + 1]
            yield text


def process_text(text, bundle_number):
    processed_text = f"##tegst-{bundle_number}##\n{text}\n##tegov-{bundle_number}##"
    return processed_text


def main():
    input_file = r"C:\Users\no2si\Downloads\eng\input.txt"
    output_file = r"C:\Users\no2si\Downloads\eng\output.txt"

    if not os.path.isfile(input_file):
        print(f"Error: {input_file} does not exist.")
        return

    with open(output_file, 'w') as out_file:
        for i, chunk in enumerate(read_file_chunks(input_file)):
            processed_chunk = process_text(chunk, i+1)
            out_file.write(processed_chunk)
            out_file.write('\n' * 15)

    print(f"Processed text saved to {output_file}")


if __name__ == "__main__":
    main()
