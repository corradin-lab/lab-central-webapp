
project_name :=lab-central-webapp
project_python_package :=lab_central_webapp

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
	nbdev_new --repo "lab-central-webapp" --branch master --user "corradin-lab" --author "An Hoang" --author_email "anhoang@wi.mit.edu" --description "Main webapp for common lab pipelines and sub-webapps" --nbs_path notebooks/package --lib_path src/lab_central_webapp

setup-post-nbdev:
	mv ._gitignore .gitignore

clean:
	rm -rf $(project_name)
	rm -rf pyproject.toml
	for file in Makefile kedro-answers.yml conf data docs logs notebooks src .gitignore README_kedro.md README.md README_nbdev.md _proc .github nbs lab_central_webapp LICENSE MANIFEST.in settings.ini setup.py;do rm -rf $$file;done


reset-project: clean generate-files setup-kedro setup-post-kedro setup-nbdev setup-post-nbdev
reset-project-with-install: clean generate-files install-packages setup-kedro setup-post-kedro setup-nbdev setup-post-nbdev
 