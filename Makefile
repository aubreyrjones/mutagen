.SUFFIXES: .odt .pdf

.odt.pdf:
	soffice --headless --convert-to pdf --outdir $(dir $?) $?

wizard: common/meta.pdf common/common.pdf pc_playbooks/wizard.pdf
	pdfunite $? pdf_output/wizard_complete.pdf

all: wizard

