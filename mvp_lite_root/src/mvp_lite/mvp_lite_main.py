import argparse

from .compute_pipeline import compute_Pipeline


def main():

    parser = argparse.ArgumentParser(
        description="Run Multi View Placement(MVP) Pipeline By Part.\n "
                    "Note: drawsheets_input.json and drawviews_input.json for part_num are "
                    "located in C:\Vectra\Auto2D_Output_Files\Temp_Data\{tool_name}\{part_num}"
    )
    parser.add_argument("part_num",
                        help="Specify the Part Number",
                        )

    args = parser.parse_args()
    # take the argument value and passed as input to the compute pipeline
    compute_Pipeline(part_num=args.part_num)