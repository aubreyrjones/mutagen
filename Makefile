.SUFFIXES: .odt .pdf

.odt.pdf:
	soffice --headless --convert-to pdf --outdir $(dir $?) $?

all: wizard sorcerer soma

wizard: common/meta.pdf common/common.pdf pc_playbooks/wizard.pdf
	pdfunite $? pdf_output/wizard_complete.pdf

sorcerer: common/meta.pdf common/common.pdf pc_playbooks/sorcerer.pdf
	pdfunite $? pdf_output/sorcerer_complete.pdf

soma: common/meta.pdf common/common.pdf pc_playbooks/soma_master.pdf
	pdfunite $? pdf_output/soma_master_complete.pdf



