"""Build static HTML site from directory of HTML templates and plain files."""
import pathlib      # necessary for using pathlib in generator
import json
import shutil
import sys
import click        # necessary for using click in generator
import jinja2


def copy_static_folders(input_dir, output_dir):
    """Copy static folders into appropriate directory."""
    static_directory_path = pathlib.Path(input_dir / "static")

    if static_directory_path.exists() and static_directory_path.is_dir():
        for item in static_directory_path.iterdir():
            dst = output_dir / item.name
            shutil.copytree(item, dst)
        print(f"Copied {static_directory_path} -> {output_dir}")


@click.command()
@click.option("-o", "--output", nargs=1, type=click.Path(exists=False),
              help='Output directory.')
@click.option("-v", "--verbose", is_flag=True, help='Print more output.')
@click.argument("input_dir", nargs=1, type=click.Path(exists=True))
def main(input_dir, output, verbose):
    """Templated static website generator."""
    input_dir = pathlib.Path(input_dir)

    if output is None:
        output = "generated_html"
    output = pathlib.Path(output)
    if output.exists():
        print(f"websitegenerator error: '{output}' already exists")
        sys.exit(1)

    config_filepath = input_dir / pathlib.Path("config.json")
    if not config_filepath.exists():
        print(f"websitegenerator error: '{config_filepath}' not found")
        sys.exit(1)
    config_list = []
    try:
        with config_filepath.open() as config_file:
            # config_filepath is open within this code block
            config_list = json.load(config_file)
        # config_filepath is automatically closed
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as e:
        print(f"websitegenerator error: '{config_filepath}'")
        print(e)
        sys.exit(1)

    for i, _ in enumerate(config_list):
        url = config_list[i]["url"]
        context_list = config_list[i]["context"]
        template_html_name = config_list[i]["template"]
        # template_directory = input_dir / "templates"
        if not pathlib.Path(input_dir / "templates").is_dir():
            print("websitegenerator error: ",
                  f"'{input_dir / "templates"}' not found")
            sys.exit(1)

        template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(input_dir / "templates"),
            autoescape=jinja2.select_autoescape(['html', 'xml']),
        )
        # template = template_env.get_template(template_html_name)
        try:
            output_text = (
                template_env.get_template(template_html_name).
                render(context_list)
            )
        except (UnicodeDecodeError, OSError, TypeError,
                jinja2.exceptions.TemplateError) as e:
            print(f"websitegenerator error: {template_html_name}")
            print(e)
            sys.exit(1)

        url = url.lstrip("/")  # remove leading slash
        output_dir = pathlib.Path(output)
        # output_path = output_dir/url/"index.html"

        (output_dir/url/"index.html").parent.mkdir(parents=True, exist_ok=True)

        with (output_dir/url/"index.html").open('w') as f:
            print(output_text, file=f)

        if verbose:
            print(f"Rendered {template_html_name} -> "
                  f"{(output_dir/url/"index.html")}")

    # Copying static folders if relevant
    copy_static_folders(input_dir, output_dir)


if __name__ == "__main__":
    main()
