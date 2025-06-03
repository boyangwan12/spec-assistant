from app.services.pdf_utils import partition_file_with_metadata
from app.utils.pdf_chunker import debug_print_sample_chunks_from_elements
import os

# Set this to the filename of your PDF in the /data directory
# Use the actual sample file path as provided
filename = os.path.join("sample_files", "Technical Specs for 500kV CCVTs for Fall 2024 Term contract complete.pdf")

if __name__ == "__main__":
    elements = partition_file_with_metadata(filename)
    debug_print_sample_chunks_from_elements(elements, max_chunks=5, merge_headings=True, sliding_window=2)
