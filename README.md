# ai_serve_chatbot_transcript_json_parser
A python code to parse AI_Serve chatbot transcript stored in json format. This is to be used after user perform AzCopy to download files onto local machine. Tested with python version 3.10.2 and 3.11.4.

# Usage
Can run the python file. It will prompt for downloaded folder. And then prompt for save folder (save folder must exists beforehand).
Another way is to use cli command. Example usage:
  - parse_download_transcript_json.py <downloaded_folder_path> <save_folder_path> <create_a_folder_on_save_folder_path_or_not (Optional) (default = False)> <include_channel_id_or_not (Optional) (default = False)>
  - parse_download_transcript_json.py /usr/local/share/downloads/my_transcripts /usr/local/work/my_transcripts/2023-11-8 True
