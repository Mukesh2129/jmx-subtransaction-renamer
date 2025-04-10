import xml.etree.ElementTree as ET
import streamlit as st
import tempfile
import os

def rename_subtransactions(jmx_input_path, jmx_output_path):
    tree = ET.parse(jmx_input_path)
    root = tree.getroot()

    all_elements = list(root.iter())
    total_transactions = 0
    total_renamed = 0

    for i, elem in enumerate(all_elements):
        if elem.tag == "TransactionController":
            transaction_name = elem.attrib.get("testname", "").strip()
            if not transaction_name:
                continue

            # Find the next hashTree sibling
            hash_tree = None
            for j in range(i + 1, len(all_elements)):
                if all_elements[j].tag == "hashTree":
                    hash_tree = all_elements[j]
                    break

            if hash_tree is None:
                continue

            sub_index = 1
            for child in list(hash_tree):
                if child.tag == "HTTPSamplerProxy":
                    new_name = f"{transaction_name}_{sub_index}"
                    child.set("testname", new_name)
                    sub_index += 1
                    total_renamed += 1

            total_transactions += 1

    tree.write(jmx_output_path, encoding="UTF-8", xml_declaration=True)
    return total_transactions, total_renamed

# Streamlit UI
st.set_page_config(page_title="JMeter Subtransaction Renamer", layout="centered")
st.title("🚀 JMeter Subtransaction Renamer")
st.markdown("Upload your `.jmx` file and this tool will rename each subtransaction under each Transaction Controller.")

uploaded_file = st.file_uploader("Upload JMX File", type=["jmx"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jmx") as tmp_input:
        tmp_input.write(uploaded_file.read())
        input_path = tmp_input.name

    output_path = input_path.replace(".jmx", "_modified.jmx")
    trans_count, renamed_count = rename_subtransactions(input_path, output_path)

    st.success(f"Renamed {renamed_count} subtransactions under {trans_count} transaction controllers.")

    with open(output_path, "rb") as f:
        st.download_button(
            label="📥 Download Modified JMX",
            data=f,
            file_name="modified_jmx_file.jmx",
            mime="application/octet-stream"
        )

    # Cleanup temp files
    os.remove(input_path)
    os.remove(output_path)