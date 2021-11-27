SOFFICE = soffice
PDFUNITE = pdfunite

-include config.mk

%.pdf : %.odt ; 
	$(SOFFICE) --headless --convert-to pdf --outdir $(dir $?) $?
	@sleep 0.25

define unite =
$(PDFUNITE) $^ $@
endef

all: wizard.pdf sorcerer.pdf soma_master.pdf gm.pdf

# Define what's common to every player's playbook.
pc_book = $(2): common/common.pdf $(1) common/meta.pdf ; $$(unite)

# Build each PC playbook. Mind the spaces: $(call  pc_book,source_playbook_sections,output_name)
$(call pc_book,pcs/wizard.pdf,wizard.pdf)
$(call pc_book,pcs/sorcerer.pdf,sorcerer.pdf)
$(call pc_book,pcs/soma_master.pdf,soma_master.pdf)

# Define what's common to every gm.
GM_Common = gm/gm.pdf common/common_gm.pdf

# Build the generic GM playbook.
gm.pdf: $(GM_Common) ; $(unite)

clean:
	@find . -name \*.pdf -exec rm {} \;


# If you're building a mutation, you can symlink your project
# directory to `mutation` and build playbooks with the same recipes as
# above.

-include mutation/all.mk
