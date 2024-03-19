try:
    import os
    import sys
    import asyncio
    import logging
    import argparse as ap
    import concurrent.futures as cf
except ModuleNotFoundError as e:
    print(f"Error: {e}")
    exit(1)


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def copy_file(source_path, target_dir):
    try:
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            logging.info(f"Created directory: [{target_dir}]")

        target_path = os.path.join(target_dir, os.path.basename(source_path))
        with open(source_path, 'rb') as src, open(target_path, 'wb') as dst:
            dst.write(src.read())
    except Exception as e:
        logging.error(f"Error copying file {source_path} to {target_dir}: {e}")


async def read_folder(source_folder, output_folder, loop):
    executor = cf.ThreadPoolExecutor(max_workers=4)
    for root, _, files in os.walk(source_folder):
        for file in files:
            file_path = os.path.join(root, file)
            _, ext = os.path.splitext(file)
            target_dir = os.path.join(output_folder, ext.lstrip('.').lower())
            logging.info(
                f"Copying the file [{file_path}] to the directory [{target_dir}]")
            await loop.run_in_executor(executor, copy_file, file_path, target_dir)


def cli():
    parser = ap.ArgumentParser(
        description='Asynchronously copy files to directories based on their extension.')
    parser.add_argument('source_folder', type=str,
                        help='The source folder to read files from.')
    parser.add_argument('output_folder', type=str,
                        help='The output folder to copy files into.')
    return parser.parse_args()


async def main():
    args = cli()
    source_folder = args.source_folder
    output_folder = args.output_folder

    if not os.path.isdir(source_folder):
        raise Exception(f"The source directory [{
                        source_folder}] does not exist or is not a directory.")

    loop = asyncio.get_running_loop()
    await read_folder(source_folder, output_folder, loop)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
