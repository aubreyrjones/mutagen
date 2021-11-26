%.pdf : %.odt ; 
	soffice --headless --convert-to pdf --outdir $(dir $?) $?
	@sleep 0.25

define unite =
pdfunite $^ $@
endef

all: wizard.pdf sorcerer.pdf soma_master.pdf gm.pdf

# Define what's common to every player's playbook.
PCC = common/meta.pdf common/common.pdf

# Build the example playbooks.
wizard.pdf: $(PCC) pcs/wizard.pdf ; $(unite)

sorcerer.pdf: $(PCC) pcs/sorcerer.pdf ; $(unite)

soma_master.pdf: $(PCC) pcs/soma_master.pdf ; $(unite)

# Define what's common to every gm.
GMC = gm/gm.pdf common/common_gm.pdf

# Build the generic GM playbook.
gm.pdf: $(GMC) ; $(unite)

clean:
	@find . -name \*.pdf -exec rm {} \;


# If you're building a mutation, you can symlink your project
# directory to `mutation` and build playbooks with the same recipes as
# above.

-include mutation/all.mk
