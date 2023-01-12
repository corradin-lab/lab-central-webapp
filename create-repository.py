import os

poetry_toml_template = \
"""
[tool.poetry]
name = "{project_name}"
version = "0.1.0"
description = "{project_description}"
authors = ["{author_email}"]

[tool.poetry.dependencies]
python = ">=3.8,<3.11"

[tool.poetry.dev-dependencies]

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.kedro]
package_name = "{python_package_name}"
project_name = "{project_human_readable_name}"
project_version = "0.18.4"

[tool.isort]
profile = "black"

[tool.coverage.report]
fail_under = 0
show_missing = true
exclude_lines = ["pragma: no cover", "raise NotImplementedError"]

"""

kedro_yml_template = \
    """
    project_name: "{project_human_readable_name}"
    repo_name: "{project_name}"
    python_package: "{python_package_name}"
    """

makefile_template = \
"""
project_name :={project_name}
project_python_package :={python_package_name}

generate-files:
	python create-repository.py

install-packages:
	poetry add --dev kedro=0.18.4 jupyter jupyterlab ruff slipcover toml pyyaml lineapy dvc wandb

setup-kedro:
	mv pyproject.toml pyproject_.toml
	kedro new -c kedro-answers.yml
	for file in $(project_name)/conf $(project_name)/data $(project_name)/docs $(project_name)/logs $(project_name)/notebooks $(project_name)/src;do mv $$file .;done 
	mv $(project_name)/README.md ./README_kedro.md
	rm -rf $(project_name)
	mv pyproject_.toml pyproject.toml

setup-post-kedro:
	cd notebooks; mkdir package exploratory analyses generate_figures && touch package/.gitkeep exploratory/.gitkeep analyses/.gitkeep generate_figures/.gitkeep ;cd ..
 
setup-nbdev:
	nbdev_new --repo "{project_name}" --branch master --user "{author_username}" --author "{author_fullname}" --author_email "{author_email}" --description "{project_description}" --nbs_path notebooks/package --lib_path src/{python_package_name}

setup-post-nbdev:
	mv ._gitignore .gitignore

clean:
	rm -rf $(project_name)
	rm -rf pyproject.toml
	for file in Makefile kedro-answers.yml conf data docs logs notebooks src .gitignore README_kedro.md README.md README_nbdev.md _proc .github nbs {python_package_name} LICENSE MANIFEST.in settings.ini setup.py;do rm -rf $$file;done


reset-project: clean generate-files setup-kedro setup-post-kedro setup-nbdev setup-post-nbdev
reset-project-with-install: clean generate-files install-packages setup-kedro setup-post-kedro setup-nbdev setup-post-nbdev
 """

key_val_dict = {}
with open("change-my-values.yaml") as file:
    for line in file.readlines():
        if len(line.split(":")) == 2:
            key_val = [ele.strip() for ele in line.strip().split(":")]
            key_val_dict[key_val[0]] = key_val[1]

key_val_dict["python_package_name"] = key_val_dict["project_name"].replace("-", "_")

#print(key_val_dict)
#print(toml_template)
with open("pyproject.toml", "w") as file:
    file.write(poetry_toml_template.format(**key_val_dict))

with open("kedro-answers.yml", "w") as file:
    file.write(kedro_yml_template.format(**key_val_dict))
    
with open("Makefile", "w") as file:
    file.write(makefile_template.format(**key_val_dict))

print("DONE!")
