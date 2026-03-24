"""
Module: gui.py
Description: A Streamlit-based GUI for managing AutoBus configuration and automation with logs.
"""
import streamlit as st
import json
import os
import sys
import subprocess
import time
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, root_path)
from module.config.config import config_manager

st.set_page_config(page_title="AutoBus v1.0.0", layout="centered")

# Initialize Session State from config file
if 'team_queue' not in st.session_state:
    config_manager.load()
    st.session_state.team_queue = config_manager.team_queue
    st.session_state.global_settings = config_manager.global_settings


def save_changes():
    """
    Writes the current team_queue and global_settings back to config.json
    """
    data = {
        "global_settings": st.session_state.global_settings,
        "team_queue": st.session_state.team_queue
    }
    with open(config_manager.CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    st.success("Settings have saved to config.json!")


# UI
st.title("AutoBus v1.0")

tab1, tab2 = st.tabs(["🚌 Dashboard", "⛓️ Team sets"])

with tab1:
    st.subheader("🚌 Dashboard")
    st.divider()

    with st.container(border=True):
        # Figures out the best way to display whatever is passed
        st.write("Run Configuration")
        st.session_state.global_settings["target_runs"] = st.number_input(
            "Total Runs",
            min_value=1,
            max_value=99,
            value=st.session_state.global_settings.get("target_runs", 1)
        )
        # Renders text in small, gray, subtle font
        st.caption("AutoBus stops once it completes total runs")

    # Execute main.py
    if st.button("Start AutoBus", type="primary"):
        # Save config first to ensure main.py reads the latest settings
        save_changes()

        # Start the main.py as a subprocess
        try:
            subprocess.Popen([sys.executable, "main.py"])
        except Exception as e:
            st.error(f"Failed to start: {e}")

    st.divider()

    st.markdown("<h3 style='text-align: center;'>🧾 AutoBus Logs</h3>", unsafe_allow_html=True)

    log_file_path = os.path.join(root_path, "logs/AutoBusLog.log")

    with st.container(border=True):
        if os.path.exists(log_file_path):
            with open(log_file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                # Show last 50 lines
                last_logs = "".join(lines[-50:])

            # Use 'st.code' for the monospace terminal look
            st.code(last_logs if last_logs else "...", language="text")

with tab2:
    if st.button("💾 Save Configuration", type="primary"):
        save_changes()

    st.subheader("⛓️ AutoBus Team Manager")
    # Button to create a NEW COPY of a team set
    if st.button("➕ Establish New Team Sets"):
        # This is the exact "copy" structure you provided
        new_team_set = {
            "team_set_name": f"New Team",
            "team_description": f"Add your description here",
            "team_preference": "teams#1",
            "buff_preference": [],
            "gift_preference": "gift1",
            "skill_preference": "skill_type1",
            "reward_preference": [],
            "road_strategy": "priority",
            "identity_preference": []
        }
        st.session_state.team_queue.append(new_team_set)
        st.rerun()

    st.divider()

    # Display each established team set in an expandable box
    for index, team in enumerate(st.session_state.team_queue):
        with st.expander(f"⛓️ Team {index + 1} : {team['team_set_name']}", expanded=True):

            # 1. Team name, description, remove button
            col_1, col_2, col_3 = st.columns([1, 2, 3])
            with col_1:
                # Remove team set
                if st.button(f"Remove Team Set {index + 1}", key=f"del_{index}"):
                    st.session_state.team_queue.pop(index)
                    st.rerun()
            with col_2:
                # Team name
                team["team_set_name"] = st.text_input(
                    "Team name: ",
                    team.get("team_set_name", ""),
                    key=f"name_{index}"
                )
            with col_3:
                # Description
                team["team_description"] = st.text_input(
                    "Team Description: ",
                    team.get("team_description", ""),
                    key=f"desc_{index}"
                )

            # 2. Team preference
            # Set options up to 6
            team_options = [f"teams#{i}" for i in range(1, 7)]
            # Get the current saved preference, default to "teams#1" if not found
            try:
                current_index = team_options.index(team.get("team_preference", "teams#1"))
            except ValueError:
                current_index = 0

            # Using selector because user can only choose 1 option
            team["team_preference"] = st.selectbox(
                "Team Preference: ",
                options=team_options,
                index=current_index,
                key=f"team_pre_{index}",
                help="Select option corresponding to 'Teams' sidebar in 'Sinners' interface"
            )

            # 3. Star buff UI
            st.write("Buff preference: ")

            # Create a map, so we can display names that user understands
            buff_map = {
                "1. Star of the Beginning": "buff1",
                "2. Cumulating Starcloud": "buff2",
                "3. Interstellar Travel": "buff3",
                "4. Star-shower": "buff4",
                "5. Binary Star-shop": "buff5",
                "6. Moon Star-shop": "buff6",
                "7. Favor of the Nebulae": "buff7",
                "8. Starlight Guidance": "buff8",
                "9. Chance comet": "buff9",
                "10. Perfected Possibility": "buff10",
            }

            current_buffs = team.get("buff_preference", [])
            # Create the UI Grid
            buff_cols = st.columns(5)
            # Initialize a new list to track what is checked
            updated_buffs = []

            for buff, (display_name, buff_id) in enumerate(buff_map.items()):
                col = buff_cols[buff % 5]  # noqa

                # Check if value(buff) exists in the current JSON file
                is_buff_checked = buff_id in current_buffs

                # Create the checkbox using the display Name and check the checkbox if
                # value exists in JSON file
                if col.checkbox(display_name, value=is_buff_checked, key=f"buff_{index}_{buff_id}"):
                    updated_buffs.append(buff_id)

            # Save the internal keys back to the team object
            team["buff_preference"] = updated_buffs

            st.divider()

            # 4. Gift preference
            st.write("Gift & Team type preference: ")
            gift_map = {
                "Burn": "gift1",
                "Bleed": "gift2",
                "Tremor": "gift3",
                "Rupture": "gift4",
                "Sinking": "gift5",
                "Poise": "gift6",
                "Charge": "gift7"
            }

            current_gift = team.get("gift_preference", "gift1")
            gift_cols = st.columns(7)

            for gift, (gift_name, gift_id) in enumerate(gift_map.items()):
                with gift_cols[gift % 7]:
                    icon_path = f"assets/ui/status_effects/{gift_id}.png"
                    st.image(icon_path, width='stretch')

                    is_gift_selected = (current_gift == gift_id)

                    if st.checkbox(gift_name, value=is_gift_selected, key=f"gift_chk_{index}_{gift_id}"):
                        if current_gift != gift_id:
                            team["gift_preference"] = gift_id
                            st.rerun()

            st.caption("Choose only one gift type!")

            st.divider()

            # 5. Skill replacing preference
            st.write("Skill replacing preference: ")
            skill_map = {
                "1. Skill 1 -> Skill 2": "skill_type1",
                "2. Skill 2 -> Skill 3": "skill_type2",
                "3. Skill 1 -> Skill 3": "skill_type3"
            }

            current_skill = team.get("skill_preference", "skill_type1")
            skill_cols = st.columns(3)
            skill_index = current_skill.index(current_skill)

            skill_name = list(skill_map.keys())
            skill_type = list(skill_map.values())

            current_index = skill_type.index(current_skill)

            # Radio button
            selected_label = st.radio(
                "Select replacement type:",
                options=skill_name,
                index=current_index,
                key=f"skill_radio_{index}",
                horizontal=True,
                label_visibility="collapsed"
            )

            team["skill_preference"] = skill_map[selected_label]

            st.divider()

            # 6. Reward preference
            reward_map = {
                "1. Ego Gift": "reward1",
                "2. Starlight": "reward2",
                "3. Cost and EGO Gift(maybe)": "reward3",
                "4. Cost": "reward4",
                "5. EGO Resources": "reward5"
            }
            current_reward_ids = team.get("reward_preference", [])

            default_display_names = []

            for saved_id in current_reward_ids:
                for name, r_id in reward_map.items():
                    if r_id == saved_id:
                        default_display_names.append(name)

            # Multi-select
            selected_names = st.multiselect(
                "Set Reward Priority:",
                options=list(reward_map.keys()),
                default=default_display_names,
                key=f"reward_multi_{index}",
                help="AutoBus checks these in order. Pick your top priority first."
            )

            team["reward_preference"] = [reward_map[name] for name in selected_names]

            st.divider()

            # 7. Road Strategy
            strategy_map = {
                "Priority Navigation": "priority",
                "Fallback Navigation": "fallback"
            }

            current_strategy = team.get("road_strategy", "priority")

            strat_display_names = list(strategy_map.keys())
            start_index = 0
            for i, (name, s_id) in enumerate(strategy_map.items()):
                if s_id == current_strategy:
                    start_index = i

            selected_name = st.radio(
                "Select navigation logic:",
                options=strat_display_names,
                index=start_index,
                key=f"road_{index}",
                horizontal=True
            )

            st.divider()

            # 8. Identity preference
            st.write("Identity select: ")
            sinner_map = {
                "Yi Sang": "sinner#1",
                "Faust": "sinner#2",
                "D Quixote": "sinner#3",
                "Ryoshu": "sinner#4",
                "Meursault": "sinner#5",
                "Hong Lu": "sinner#6",
                "Heathcliff": "sinner#7",
                "Ishmael": "sinner#8",
                "Rodion": "sinner#9",
                "Sinclair": "sinner#10",
                "Outis": "sinner#11",
                "Gregor": "sinner#12"
            }
            current_identities = team.get("identity_preference", [])
            sinner_cols = st.columns(6)

            for sinner, (name, s_id) in enumerate(sinner_map.items()):
                col = sinner_cols[sinner % 6]
                with col:
                    st.image(f"assets/ui/sinners/photo/{s_id}.png", width='stretch')
                    is_sinner_selected = s_id in current_identities

                    # Using priority_num to show user the identities selection order
                    label = name
                    if is_sinner_selected:
                        priority_num = current_identities.index(s_id) + 1
                        label = f"#{priority_num} {name}"

                    if st.checkbox(label, value=is_sinner_selected, key=f"sinner_{index}_{s_id}"):
                        # If checked, goes to the end of the list
                        if s_id not in current_identities:
                            current_identities.append(s_id)
                            st.rerun()
                    else:
                        # If unchecked, remove from list
                        if s_id in current_identities:
                            current_identities.remove(s_id)
                            st.rerun()

            team["identity_preference"] = current_identities

# Add a sidebar as a control panel, use this method to prevent keep refreshing
# so tab 2 (Team Sets) completely disappeared
with st.sidebar:
    st.title("⚙️ Control Panel")
    st.divider()

    do_refresh = st.checkbox("Enable Live Log Update", value=False)

    st.image("assets/ui/Ryoshu/r3.png", width='stretch')

    if do_refresh:
        time.sleep(3)
        st.rerun()

    st.info("Note: Enable live log update will force you return to dashboard every 3 seconds")
