#!/usr/bin/python3 -tt
# Project: naf_framework_solution_wizard
# Filename: naf_framework_solution_wizard.py
# claudiadeluna
# PyCharm

__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "11/25/25"
__copyright__ = "Copyright (c) 2025 Claudia"
__license__ = "Python"


import utils
import streamlit as st


def main() -> None:
    """Landing page for the NAF NAF Solution Wizard.

    This page orients users to the Solution Wizard functionality.
    """

    st.set_page_config(
        page_title="NAF Framework Solution Wizard",
        page_icon="images/naf_favicon-96x96.png",
        layout="wide",
    )

    # Shared sidebar branding
    utils.render_global_sidebar()

    st.title("Network Automation Forum (NAF) Framework Solution Wizard")
    st.markdown(
        """
        This application helps you apply the Network Automation Forum's
        **Network Automation Framework** to your automation projects.
        
        Use the **Solution Wizard** to describe how you plan on designing your automation solution:
        """
    )

    # Intro: two-column layout (left: diagram, right: description)
    col_img, col_text = st.columns([1, 1])
    with col_img:
        st.image(
            "images/naf_arch_framework_figure2.png",
            width="stretch",
        )
        st.caption(
            "Source: https://github.com/Network-Automation-Forum/reference/blob/main/docs/Framework/Framework.md"
        )

    with col_text:
        st.subheader("Solution Wizard")
        st.markdown(
            """
            Define the **WHY, WHO, HOW, and WHAT** of your automation project using the NAF
            [Network Automation Framework](https://reference.networkautomation.forum/Framework/Framework/).

            The wizard guides structured thinking across every NAF component — stakeholders, scope,
            data flows, and build/buy/support decisions — so nothing critical is missed. Your
            selections generate a shareable solution design document for your team, stakeholders,
            and management.
            """
        )
        st.caption(
            "Tip: If you can't answer a question technically, note that the function is needed and use the Custom option to describe what you can."
        )

    # CTA button — placed before the detail sections so it's visible without scrolling
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Building Your Solution", type="primary", use_container_width=True):
            st.switch_page("pages/20_NAF_Solution_Wizard.py")

    st.markdown("### Design Your Automation Solution")

    with st.expander("What does the wizard cover?", expanded=False):
        st.markdown(
            """
**Project context:** Initiative (problem, scope, deployment), Stakeholders, My Role, Dependencies, and Timeline.

**NAF Components:** Presentation, Intent, Observability, Orchestration, Collector, and Executor.

The wizard generates a **complete solution design document** (JSON + Markdown + timeline) you can share with team members, stakeholders, management, and other IT teams.
            """
        )

    with st.expander("Saving and loading your work", expanded=False):
        st.markdown(
            """
Save your work as a JSON file and load it later to continue editing. The JSON contains all wizard inputs and can be shared with others. Use the **Load Session** button in the Solution Wizard sidebar to restore a saved design.
            """
        )


if __name__ == "__main__":
    main()
    st.markdown("---")
    st.caption(
        "Disclaimer: Results depend entirely on your inputs. Validate data and use professional judgment."
    )

    with st.expander("⚠️ Read full disclaimer", expanded=False):
        st.markdown(
            """
            The calculations, outputs, and recommendations presented by this application are for informational purposes only. 
            Results are entirely dependent on the inputs provided by the user and any assumptions entered. 
            It is the user's responsibility to validate all inputs, review the outputs for accuracy and suitability, and apply appropriate professional judgment before making decisions based on these results.
            
            By using this application, you acknowledge and agree that:
            - You are solely responsible for the data you enter and for any conclusions or decisions you draw from the results.
            - The authors and contributors make no warranties, express or implied, regarding accuracy, completeness, or fitness for a particular purpose.
            - The authors and contributors shall not be liable for any losses or damages arising from use of or reliance on the results.
            """
        )

    st.markdown("---")
    
    # Sponsored by EIA section
    col_logo, col_links = st.columns([1, 3])
    with col_logo:
        # Get base64 encoded image
        logo_base64 = utils.get_image_base64("images/EIA Logo FINAL small_Round.png")
        if logo_base64:
            st.markdown(
                f'[<img src="data:image/png;base64,{logo_base64}" width="50%">](https://eianow.com)',
                unsafe_allow_html=True
            )
        else:
            # Fallback to non-clickable image if base64 fails
            st.image("images/EIA Logo FINAL small_Round.png", width=50)
    
    with col_links:
        st.markdown("### Sponsored by EIA")
        st.markdown("[🏠 EIA Home](https://eianow.com) | [[in] EIA on LinkedIn](https://www.linkedin.com/company/eianow/)")
