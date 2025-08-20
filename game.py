from flask import Flask, render_template, request, jsonify, session
import os
import json
from datetime import datetime, timedelta
import random
import math

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

# Game constants - significantly increased difficulty
CLICK_BASE_VALUE = 1
UPGRADE_MULTIPLIER = 1.15  # Reduced from 1.5 for more gradual scaling with many more levels
PASSIVE_INCOME_INTERVAL = 1  # seconds
PRESTIGE_REQUIREMENT = 1_000_000_000  # Increased to 1 billion lines
MAX_UPGRADE_LEVEL = 1000  # New default max level for most upgrades
MAX_ASSET_LEVEL = 500  # New default max level for most assets

# Extended list of upgrades with vastly increased costs and progression curve
UPGRADES = {
    # TIER 1: Basic Tools (0-1k lines) - Early Game
    'notepad': {
        'name': 'Notepad',
        'description': 'The most basic text editor',
        'base_cost': 10,
        'click_bonus': 0.2,
        'icon': 'notepad.png',
        'max_level': MAX_UPGRADE_LEVEL,
        'tier': 1
    },
    'better_keyboard': {
        'name': 'Better Keyboard',
        'description': 'Type faster with a mechanical keyboard',
        'base_cost': 50,
        'click_bonus': 0.5,
        'icon': 'keyboard.png',
        'max_level': MAX_UPGRADE_LEVEL,
        'tier': 1
    },
    'syntax_highlighting': {
        'name': 'Syntax Highlighting',
        'description': 'Colors make code more readable',
        'base_cost': 200,
        'click_bonus': 1,
        'icon': 'syntax.png',
        'max_level': MAX_UPGRADE_LEVEL,
        'tier': 1
    },
    'code_snippets': {
        'name': 'Code Snippets',
        'description': 'Reuse common code patterns',
        'base_cost': 500,
        'click_bonus': 2,
        'icon': 'snippet.png',
        'max_level': MAX_UPGRADE_LEVEL,
        'tier': 1
    },
    'autocomplete': {
        'name': 'Auto-Complete',
        'description': 'Suggestions as you type',
        'base_cost': 1_000,
        'click_bonus': 3,
        'icon': 'autocomplete.png',
        'max_level': MAX_UPGRADE_LEVEL,
        'tier': 1
    },
    
    # TIER 2: IDE Features (1k-10k lines) - Early-Mid Game
    'error_detection': {
        'name': 'Error Detection',
        'description': 'Find errors before running the code',
        'base_cost': 2_500,
        'click_bonus': 5,
        'icon': 'error.png',
        'max_level': MAX_UPGRADE_LEVEL,
        'tier': 2
    },
    'ide_plugins': {
        'name': 'IDE Plugins',
        'description': 'Enhance productivity with plugins',
        'base_cost': 5_000,
        'click_bonus': 10,
        'icon': 'plugin.png',
        'max_level': MAX_UPGRADE_LEVEL,
        'tier': 2
    },
    'version_control': {
        'name': 'Version Control',
        'description': 'Track changes in your code',
        'base_cost': 10_000,
        'click_bonus': 15,
        'icon': 'git.png',
        'max_level': MAX_UPGRADE_LEVEL,
        'tier': 2
    },
    'linter': {
        'name': 'Code Linter',
        'description': 'Automatically fix code style issues',
        'base_cost': 25_000,
        'click_bonus': 25,
        'icon': 'linter.png',
        'max_level': MAX_UPGRADE_LEVEL,
        'tier': 2
    },
    'debugger': {
        'name': 'Debugger',
        'description': 'Step through code to find bugs',
        'base_cost': 50_000,
        'click_bonus': 40,
        'icon': 'debug.png',
        'max_level': MAX_UPGRADE_LEVEL,
        'tier': 2
    },
    
    # TIER 3: Professional Tools (10k-100k lines) - Mid Game
    'code_formatter': {
        'name': 'Code Formatter',
        'description': 'Maintain consistent code style',
        'base_cost': 100_000,
        'click_bonus': 60,
        'icon': 'format.png',
        'max_level': MAX_UPGRADE_LEVEL,
        'tier': 3
    },
    'test_framework': {
        'name': 'Test Framework',
        'description': 'Automate code testing',
        'base_cost': 250_000,
        'click_bonus': 80,
        'icon': 'test.png',
        'max_level': MAX_UPGRADE_LEVEL,
        'tier': 3
    },
    'pair_programming': {
        'name': 'Pair Programming',
        'description': 'Two programmers, one keyboard',
        'base_cost': 500_000,
        'click_bonus': 120,
        'icon': 'pair.png',
        'max_level': MAX_UPGRADE_LEVEL,
        'tier': 3
    },
    'code_review_tools': {
        'name': 'Code Review Tools',
        'description': 'Improve code quality with peer feedback',
        'base_cost': 1_000_000,
        'click_bonus': 200,
        'icon': 'review.png',
        'max_level': MAX_UPGRADE_LEVEL,
        'tier': 3
    },
    'continuous_integration': {
        'name': 'Continuous Integration',
        'description': 'Automatically build and test code',
        'base_cost': 2_500_000,
        'click_bonus': 350,
        'icon': 'ci.png',
        'max_level': MAX_UPGRADE_LEVEL,
        'tier': 3
    },
    
    # TIER 4: Advanced Technologies (100k-1M lines) - Mid-Late Game
    'ai_assistant': {
        'name': 'AI Assistant',
        'description': 'Get coding help from AI',
        'base_cost': 5_000_000,
        'click_bonus': 500,
        'icon': 'ai.png',
        'max_level': MAX_UPGRADE_LEVEL,
        'tier': 4
    },
    'code_generation': {
        'name': 'Code Generation',
        'description': 'Generate boilerplate code automatically',
        'base_cost': 10_000_000,
        'click_bonus': 800,
        'icon': 'generate.png',
        'max_level': MAX_UPGRADE_LEVEL,
        'tier': 4
    },
    'smart_refactoring': {
        'name': 'Smart Refactoring',
        'description': 'AI-assisted code restructuring',
        'base_cost': 25_000_000,
        'click_bonus': 1_200,
        'icon': 'refactor-smart.png',
        'max_level': MAX_UPGRADE_LEVEL,
        'tier': 4
    },
    'adaptive_compiler': {
        'name': 'Adaptive Compiler',
        'description': 'Compiler that learns your coding patterns',
        'base_cost': 50_000_000,
        'click_bonus': 2_000,
        'icon': 'compiler.png',
        'max_level': MAX_UPGRADE_LEVEL,
        'tier': 4
    },
    'neural_optimizer': {
        'name': 'Neural Code Optimizer',
        'description': 'Neural network optimization of your code',
        'base_cost': 100_000_000,
        'click_bonus': 3_500,
        'icon': 'optimizer.png',
        'max_level': MAX_UPGRADE_LEVEL,
        'tier': 4
    },
    
    # TIER 5: Future Tech (1M-100M lines) - Late Game
    'quantum_keyboard': {
        'name': 'Quantum Keyboard',
        'description': 'Type in multiple universes simultaneously',
        'base_cost': 250_000_000,
        'click_bonus': 5_000,
        'icon': 'quantum.png',
        'max_level': 500,
        'tier': 5
    },
    'thought_interface': {
        'name': 'Thought Interface',
        'description': 'Code directly from your thoughts',
        'base_cost': 500_000_000,
        'click_bonus': 8_000,
        'icon': 'thought.png',
        'max_level': 500,
        'tier': 5
    },
    'automatic_refactoring': {
        'name': 'Automatic Refactoring',
        'description': 'Your code refactors itself for better efficiency',
        'base_cost': 1_000_000_000,
        'click_bonus': 15_000,
        'icon': 'refactor.png',
        'max_level': 500,
        'tier': 5
    },
    'holographic_interface': {
        'name': 'Holographic Interface',
        'description': 'Manipulate code in 3D space',
        'base_cost': 5_000_000_000,
        'click_bonus': 30_000,
        'icon': 'hologram.png',
        'max_level': 300,
        'tier': 5
    },
    
    # TIER 6: Sci-Fi Tech (100M-10B lines) - End Game
    'time_manipulation_ide': {
        'name': 'Time-Manipulation IDE',
        'description': 'Slow down time to code faster than humanly possible',
        'base_cost': 10_000_000_000,
        'click_bonus': 50_000,
        'icon': 'time.png',
        'max_level': 200,
        'tier': 6
    },
    'quantum_computing': {
        'name': 'Quantum Computing',
        'description': 'Harness quantum superposition for coding',
        'base_cost': 50_000_000_000,
        'click_bonus': 100_000,
        'icon': 'quantum-computer.png',
        'max_level': 200,
        'tier': 6
    },
    'consciousness_upload': {
        'name': 'Consciousness Upload',
        'description': 'Become one with your code',
        'base_cost': 100_000_000_000,
        'click_bonus': 250_000,
        'icon': 'upload.png',
        'max_level': 150,
        'tier': 6
    },
    'reality_compiler': {
        'name': 'Reality Compiler',
        'description': 'Your code directly alters reality',
        'base_cost': 500_000_000_000,
        'click_bonus': 500_000,
        'icon': 'reality.png',
        'max_level': 100,
        'tier': 6
    },
    'universal_programmer': {
        'name': 'Universal Programmer',
        'description': 'Program the fundamental laws of the universe',
        'base_cost': 1_000_000_000_000,
        'click_bonus': 1_000_000,
        'icon': 'universe.png',
        'max_level': 10,
        'tier': 6
    }
}

# Extended list of passive assets with increased costs and progression curve
PASSIVE_ASSETS = {
    # TIER 1: Basic Staff (0-1k lines) - Early Game
    'intern': {
        'name': 'Intern',
        'description': 'Hires a coding intern',
        'base_cost': 100,
        'income': 0.1,
        'icon': 'intern.png',
        'max_level': MAX_ASSET_LEVEL,
        'tier': 1
    },
    'student_coder': {
        'name': 'Student Coder',
        'description': 'Part-time student looking for experience',
        'base_cost': 250,
        'income': 0.3,
        'icon': 'student.png',
        'max_level': MAX_ASSET_LEVEL,
        'tier': 1
    },
    'code_bootcamp_grad': {
        'name': 'Bootcamp Graduate',
        'description': 'Recently completed a coding bootcamp',
        'base_cost': 500,
        'income': 0.6,
        'icon': 'bootcamp.png',
        'max_level': MAX_ASSET_LEVEL,
        'tier': 1
    },
    'junior_dev': {
        'name': 'Junior Developer',
        'description': 'Hires a junior programmer',
        'base_cost': 1_000,
        'income': 1.2,
        'icon': 'junior.png',
        'max_level': MAX_ASSET_LEVEL,
        'tier': 1
    },
    
    # TIER 2: Professional Staff (1k-10k lines) - Early-Mid Game
    'mid_level_dev': {
        'name': 'Mid-Level Developer',
        'description': 'Developer with a few years of experience',
        'base_cost': 2_500,
        'income': 2.5,
        'icon': 'mid.png',
        'max_level': MAX_ASSET_LEVEL,
        'tier': 2
    },
    'qa_engineer': {
        'name': 'QA Engineer',
        'description': 'Finds and fixes bugs before they cause problems',
        'base_cost': 5_000,
        'income': 4,
        'icon': 'qa.png',
        'max_level': MAX_ASSET_LEVEL,
        'tier': 2
    },
    'devops_specialist': {
        'name': 'DevOps Specialist',
        'description': 'Streamlines your development pipeline',
        'base_cost': 10_000,
        'income': 7,
        'icon': 'devops.png',
        'max_level': MAX_ASSET_LEVEL,
        'tier': 2
    },
    'senior_dev': {
        'name': 'Senior Developer',
        'description': 'Hires an experienced programmer',
        'base_cost': 25_000,
        'income': 12,
        'icon': 'senior.png',
        'max_level': MAX_ASSET_LEVEL,
        'tier': 2
    },
    
    # TIER 3: Team Structure (10k-100k lines) - Mid Game
    'frontend_team': {
        'name': 'Frontend Team',
        'description': 'Specialized in user interfaces',
        'base_cost': 50_000,
        'income': 20,
        'icon': 'frontend.png',
        'max_level': MAX_ASSET_LEVEL,
        'tier': 3
    },
    'backend_team': {
        'name': 'Backend Team',
        'description': 'Specialized in server-side code',
        'base_cost': 100_000,
        'income': 35,
        'icon': 'backend.png',
        'max_level': MAX_ASSET_LEVEL,
        'tier': 3
    },
    'mobile_team': {
        'name': 'Mobile Dev Team',
        'description': 'Specialized in mobile applications',
        'base_cost': 250_000,
        'income': 60,
        'icon': 'mobile.png',
        'max_level': MAX_ASSET_LEVEL,
        'tier': 3
    },
    'dev_team': {
        'name': 'Full Dev Team',
        'description': 'Hires a whole team of developers',
        'base_cost': 500_000,
        'income': 100,
        'icon': 'team.png',
        'max_level': MAX_ASSET_LEVEL,
        'tier': 3
    },
    
    # TIER 4: Organization Structure (100k-1M lines) - Mid-Late Game
    'development_department': {
        'name': 'Development Department',
        'description': 'A full department dedicated to coding',
        'base_cost': 1_000_000,
        'income': 175,
        'icon': 'department.png',
        'max_level': MAX_ASSET_LEVEL,
        'tier': 4
    },
    'research_division': {
        'name': 'R&D Division',
        'description': 'Pushing the boundaries of what\'s possible',
        'base_cost': 2_500_000,
        'income': 300,
        'icon': 'research.png',
        'max_level': MAX_ASSET_LEVEL,
        'tier': 4
    },
    'ai_tools_division': {
        'name': 'AI Tools Division',
        'description': 'Creating AI-powered development tools',
        'base_cost': 5_000_000,
        'income': 500,
        'icon': 'ai-tools.png',
        'max_level': MAX_ASSET_LEVEL,
        'tier': 4
    },
    'ai_cluster': {
        'name': 'AI Code Cluster',
        'description': 'Deploys AI to write code continuously',
        'base_cost': 10_000_000,
        'income': 800,
        'icon': 'cluster.png',
        'max_level': MAX_ASSET_LEVEL,
        'tier': 4
    },
    
    # TIER 5: Future Tech Teams (1M-100M lines) - Late Game
    'quantum_team': {
        'name': 'Quantum Programming Team',
        'description': 'Specializes in quantum algorithms',
        'base_cost': 25_000_000,
        'income': 1_500,
        'icon': 'quantum-team.png',
        'max_level': 300,
        'tier': 5
    },
    'neural_interface_lab': {
        'name': 'Neural Interface Lab',
        'description': 'Developing direct brain-to-code interfaces',
        'base_cost': 50_000_000,
        'income': 3_000,
        'icon': 'neural-lab.png',
        'max_level': 300,
        'tier': 5
    },
    'quantum_server': {
        'name': 'Quantum Server Farm',
        'description': 'Computes code in parallel universes',
        'base_cost': 100_000_000,
        'income': 5_000,
        'icon': 'quantum-server.png',
        'max_level': 250,
        'tier': 5
    },
    
    # TIER 6: Sci-Fi Organizations (100M-10B lines) - End Game
    'code_generators': {
        'name': 'Neural Code Generators',
        'description': 'Advanced neural networks that generate entire codebases',
        'base_cost': 250_000_000,
        'income': 10_000,
        'icon': 'neural.png',
        'max_level': 200,
        'tier': 6
    },
    'sentient_code_colony': {
        'name': 'Sentient Code Colony',
        'description': 'Self-aware code that writes more of itself',
        'base_cost': 500_000_000,
        'income': 20_000,
        'icon': 'sentient.png',
        'max_level': 150,
        'tier': 6
    },
    'time_loop_systems': {
        'name': 'Time Loop Systems',
        'description': 'Code written in the future sent back to now',
        'base_cost': 1_000_000_000,
        'income': 40_000,
        'icon': 'timeloop.png',
        'max_level': 100,
        'tier': 6
    },
    'multiverse_coding_network': {
        'name': 'Multiverse Coding Network',
        'description': 'Collaborative coding across parallel universes',
        'base_cost': 5_000_000_000,
        'income': 100_000,
        'icon': 'multiverse.png',
        'max_level': 50,
        'tier': 6
    },
    'cosmic_code_entity': {
        'name': 'Cosmic Code Entity',
        'description': 'A being of pure code extending across space-time',
        'base_cost': 10_000_000_000,
        'income': 250_000,
        'icon': 'cosmic.png',
        'max_level': 10,
        'tier': 6
    }
}

# Revamped themes with vastly increased thresholds
THEMES = {
    0: {
        'name': 'Notepad',
        'description': 'Basic text editor',
        'css': 'notepad.css'
    },
    10_000: {
        'name': 'Terminal',
        'description': 'Command line interface',
        'css': 'terminal.css'
    },
    1_000_000: {
        'name': 'IDE Basic',
        'description': 'Simple integrated development environment',
        'css': 'ide_basic.css'
    },
    100_000_000: {
        'name': 'Modern IDE',
        'description': 'Professional development environment',
        'css': 'modern_ide.css'
    },
    10_000_000_000: {
        'name': 'Futuristic Interface',
        'description': 'Next-gen programming interface',
        'css': 'futuristic.css'
    },
    1_000_000_000_000: {
        'name': 'Virtual Holographic',
        'description': 'Holographic programming experience',
        'css': 'holographic.css'
    }
}

ACHIEVEMENTS = {
    'first_line': {
        'name': 'Hello World',
        'description': 'Write your first line of code',
        'icon': 'achievement_first.png',
        'requirement': lambda state: state['lines_of_code'] >= 1,
        'reward': None
    },
    'hundred_lines': {
        'name': 'Code Apprentice',
        'description': 'Write 100 lines of code',
        'icon': 'achievement_100.png',
        'requirement': lambda state: state['lines_of_code'] >= 100,
        'reward': {'click_bonus': 1}
    },
    'thousand_lines': {
        'name': 'Code Journeyman',
        'description': 'Write 1,000 lines of code',
        'icon': 'achievement_1k.png',
        'requirement': lambda state: state['lines_of_code'] >= 1000,
        'reward': {'click_bonus': 5}
    },
    'million_lines': {
        'name': 'Code Master',
        'description': 'Write 1,000,000 lines of code',
        'icon': 'achievement_1m.png',
        'requirement': lambda state: state['lines_of_code'] >= 1000000,
        'reward': {'click_bonus': 100}
    },
    'first_upgrade': {
        'name': 'Tooling Up',
        'description': 'Purchase your first upgrade',
        'icon': 'achievement_upgrade.png',
        'requirement': lambda state: any(level > 0 for level in state['upgrades'].values()),
        'reward': None
    },
    'all_basic_upgrades': {
        'name': 'Well-Equipped',
        'description': 'Get at least one level in each basic upgrade',
        'icon': 'achievement_all_upgrades.png',
        'requirement': lambda state: all(state['upgrades'].get(key, 0) > 0 for key in ['better_keyboard', 'code_snippets', 'ide_plugins']),
        'reward': {'passive_bonus': 0.5}
    },
    'max_upgrade': {
        'name': 'Maximized Efficiency',
        'description': 'Max out any upgrade',
        'icon': 'achievement_max.png',
        'requirement': lambda state: any(state['upgrades'].get(key, 0) >= UPGRADES[key]['max_level'] for key in UPGRADES),
        'reward': {'click_bonus': 50}
    },
    'first_asset': {
        'name': 'Team Builder',
        'description': 'Hire your first team member',
        'icon': 'achievement_team.png',
        'requirement': lambda state: any(level > 0 for level in state['passive_assets'].values()),
        'reward': None
    },
    'all_basic_assets': {
        'name': 'Full Squad',
        'description': 'Hire at least one of each basic asset',
        'icon': 'achievement_all_assets.png',
        'requirement': lambda state: all(state['passive_assets'].get(key, 0) > 0 for key in ['intern', 'junior_dev', 'senior_dev']),
        'reward': {'click_bonus': 10}
    },
    'max_asset': {
        'name': 'HR Master',
        'description': 'Max out any passive asset',
        'icon': 'achievement_max_asset.png',
        'requirement': lambda state: any(state['passive_assets'].get(key, 0) >= PASSIVE_ASSETS[key]['max_level'] for key in PASSIVE_ASSETS),
        'reward': {'passive_multiplier': 1.5}
    },
    'first_prestige': {
        'name': 'Reborn Coder',
        'description': 'Prestige for the first time',
        'icon': 'achievement_prestige.png',
        'requirement': lambda state: state['prestige_level'] >= 1,
        'reward': {'prestige_bonus': 0.1}
    },
    'five_prestiges': {
        'name': 'Code Immortal',
        'description': 'Prestige five times',
        'icon': 'achievement_prestige5.png',
        'requirement': lambda state: state['prestige_level'] >= 5,
        'reward': {'prestige_bonus': 0.5}
    },
    'speed_demon': {
        'name': 'Speed Demon',
        'description': 'Reach 1,000 lines per click',
        'icon': 'achievement_speed.png',
        'requirement': lambda state: state['code_per_click'] >= 1000,
        'reward': {'click_multiplier': 1.25}
    },
    'passive_master': {
        'name': 'Passive Income Master',
        'description': 'Reach 1,000 lines per second',
        'icon': 'achievement_passive.png',
        'requirement': lambda state: state['code_per_second'] >= 1000,
        'reward': {'passive_multiplier': 2}
    },
    'keyboard_warrior': {
        'name': 'Keyboard Warrior',
        'description': 'Click 1,000 times',
        'icon': 'achievement_clicks.png',
        'requirement': lambda state: state.get('total_clicks', 0) >= 1000,
        'reward': {'click_multiplier': 1.1}
    },
    'overnight_coder': {
        'name': 'Overnight Coder',
        'description': 'Let passive income generate for at least 8 hours',
        'icon': 'achievement_overnight.png',
        'requirement': lambda state: state.get('longest_session', 0) >= 8 * 3600,
        'reward': {'passive_multiplier': 1.2}
    }
}

SPECIAL_EVENTS = {
    'bug_found': {
        'name': 'Bug Found!',
        'description': 'A critical bug was found in your code. Fix it quickly!',
        'action': 'Click rapidly to fix',
        'reward': {'temporary_click_multiplier': 5, 'duration': 10},
        'failure': {'lines_penalty': 0.05}
    },
    'code_review': {
        'name': 'Code Review',
        'description': 'Your code is being reviewed. Make improvements to impress your peers.',
        'action': 'Purchase an upgrade',
        'reward': {'lines_bonus': 0.2, 'duration': 30},
        'failure': {'production_penalty': 0.5, 'duration': 20}
    },
    'hackathon': {
        'name': 'Hackathon',
        'description': 'A coding hackathon is happening! Show off your skills!',
        'action': 'Reach target lines in time',
        'target': lambda state: state['lines_of_code'] * 1.2,
        'time_limit': 60,
        'reward': {'new_upgrade_unlock': 'hackathon_trophy'},
        'failure': None
    }
}

def get_new_game_state():
    return {
        'lines_of_code': 0,
        'prestige_level': 0,
        'prestige_multiplier': 1,
        'code_per_click': CLICK_BASE_VALUE,
        'code_per_second': 0,
        'upgrades': {k: 0 for k in UPGRADES.keys()},
        'passive_assets': {k: 0 for k in PASSIVE_ASSETS.keys()},
        'last_tick': datetime.now().timestamp(),
        'theme': 'notepad.css',
        'achievements': [],
        'total_clicks': 0,
        'longest_session': 0,
        'last_session_start': datetime.now().timestamp(),
        'active_events': [],
        'temporary_multipliers': {},
        'bulk_buy_mode': {'upgrades': 1, 'assets': 1},  # Default to buying 1 at a time
        'stats': {
            'total_lines_written': 0,
            'total_lines_from_clicks': 0,
            'total_lines_from_passive': 0,
            'total_prestiges': 0,
            'highest_lines_per_click': 0,
            'highest_lines_per_second': 0,
            'upgrades_purchased': 0,
            'assets_purchased': 0
        }
    }

def check_achievements(game_state):
    """Check for newly unlocked achievements"""
    unlocked = []
    for achievement_id, achievement in ACHIEVEMENTS.items():
        # Skip already unlocked achievements
        if achievement_id in game_state['achievements']:
            continue
        
        # Check if the achievement is unlocked now
        if achievement['requirement'](game_state):
            game_state['achievements'].append(achievement_id)
            unlocked.append(achievement_id)
            
            # Apply rewards if any
            if achievement['reward']:
                apply_achievement_reward(game_state, achievement['reward'])
    
    return unlocked

def apply_achievement_reward(game_state, reward):
    """Apply rewards from achievements"""
    if 'click_bonus' in reward:
        # Add flat bonus to click power
        game_state['code_per_click'] += reward['click_bonus']
    
    if 'click_multiplier' in reward:
        # Multiply current click power
        game_state['code_per_click'] *= reward['click_multiplier']
    
    if 'passive_bonus' in reward:
        # Add flat bonus to passive income
        game_state['code_per_second'] += reward['passive_bonus']
    
    if 'passive_multiplier' in reward:
        # Multiply passive income
        game_state['code_per_second'] *= reward['passive_multiplier']
    
    if 'prestige_bonus' in reward:
        # Add to prestige multiplier
        game_state['prestige_multiplier'] += reward['prestige_bonus']

def update_session_time(game_state):
    """Update the session time tracking"""
    current_time = datetime.now().timestamp()
    session_length = current_time - game_state['last_session_start']
    
    # If this is a new session (more than 30 min gap)
    if session_length > 1800:
        game_state['last_session_start'] = current_time
    else:
        # Update longest session if current one is longer
        if session_length > game_state['longest_session']:
            game_state['longest_session'] = session_length

def trigger_random_event(game_state):
    """Occasionally trigger a special event"""
    # Only trigger if there are no active events
    if not game_state['active_events'] and random.random() < 0.01:  # 1% chance per click
        event_key = random.choice(list(SPECIAL_EVENTS.keys()))
        event = SPECIAL_EVENTS[event_key]
        
        # Customize event based on current game state
        if event_key == 'hackathon':
            target = game_state['lines_of_code'] * 1.2
            event_data = {
                'id': event_key,
                'name': event['name'],
                'description': event['description'],
                'action': event['action'],
                'target': target,
                'end_time': datetime.now().timestamp() + event['time_limit'],
                'completed': False
            }
        else:
            event_data = {
                'id': event_key,
                'name': event['name'],
                'description': event['description'],
                'action': event['action'],
                'end_time': datetime.now().timestamp() + 60,  # Default 1 minute
                'completed': False
            }
        
        game_state['active_events'].append(event_data)
        return event_data
    
    return None

@app.route('/')
def index():
    if 'game_state' not in session:
        session['game_state'] = get_new_game_state()
    
    # Calculate current theme based on progress
    game_state = session['game_state']
    update_session_time(game_state)
    
    # Check achievements
    new_achievements = check_achievements(game_state)
    
    lines_of_code_total = game_state['lines_of_code']
    current_theme = THEMES[0]['css']
    
    # Find current theme
    for threshold, theme in sorted(THEMES.items()):
        if lines_of_code_total >= threshold:
            current_theme = theme['css']
        else:
            break
    
    game_state['theme'] = current_theme
    session['game_state'] = game_state
    
    # Create a serializable version of achievements without lambda functions
    serializable_achievements = {}
    for achievement_id, achievement in ACHIEVEMENTS.items():
        serializable_achievement = achievement.copy()
        # Remove the non-serializable lambda function
        if 'requirement' in serializable_achievement:
            del serializable_achievement['requirement']
        serializable_achievements[achievement_id] = serializable_achievement
    
    # Pass constants to template for client-side use
    return render_template('game.html', 
                          game_state=json.dumps(game_state), 
                          theme=current_theme,
                          upgrades=UPGRADES, 
                          passive_assets=PASSIVE_ASSETS,
                          themes=THEMES,
                          achievements=serializable_achievements,
                          new_achievements=new_achievements,
                          upgrade_multiplier=UPGRADE_MULTIPLIER,
                          prestige_requirement=PRESTIGE_REQUIREMENT)

@app.route('/click', methods=['POST'])
def click():
    if 'game_state' not in session:
        session['game_state'] = get_new_game_state()
    
    game_state = session['game_state']
    
    # Track clicks - make sure to initialize if it doesn't exist
    if 'total_clicks' not in game_state:
        game_state['total_clicks'] = 0
    game_state['total_clicks'] += 1
    
    # Make sure stats object exists
    if 'stats' not in game_state:
        game_state['stats'] = {}
    
    # Track clicks in stats too
    if 'total_clicks' not in game_state['stats']:
        game_state['stats']['total_clicks'] = 0
    game_state['stats']['total_clicks'] += 1
    
    # Check for active temporary multipliers
    current_time = datetime.now().timestamp()
    click_multiplier = 1
    
    for mult_id, mult_data in list(game_state.get('temporary_multipliers', {}).items()):
        if current_time > mult_data['end_time']:
            # Remove expired multiplier
            del game_state['temporary_multipliers'][mult_id]
        elif mult_id == 'click':
            click_multiplier *= mult_data['value']
    
    # Add lines from click with any temporary multipliers
    base_click_value = game_state['code_per_click']
    actual_click_value = base_click_value * click_multiplier
    game_state['lines_of_code'] += actual_click_value
    
    # Update stats
    game_state['stats']['total_lines_written'] += actual_click_value
    game_state['stats']['total_lines_from_clicks'] += actual_click_value
    if base_click_value > game_state['stats']['highest_lines_per_click']:
        game_state['stats']['highest_lines_per_click'] = base_click_value
    
    # Calculate passive income since last tick
    current_time = datetime.now().timestamp()
    time_diff = current_time - game_state['last_tick']
    
    # Check for passive income multipliers
    passive_multiplier = 1
    for mult_id, mult_data in list(game_state.get('temporary_multipliers', {}).items()):
        if mult_id == 'passive':
            passive_multiplier *= mult_data['value']
    
    passive_income = game_state['code_per_second'] * passive_multiplier * time_diff
    game_state['lines_of_code'] += passive_income
    game_state['last_tick'] = current_time
    
    # Update stats for passive income
    game_state['stats']['total_lines_written'] += passive_income
    game_state['stats']['total_lines_from_passive'] += passive_income
    
    # Update session time
    update_session_time(game_state)
    
    # Check for achievements
    new_achievements = check_achievements(game_state)
    
    # Chance to trigger a random event
    new_event = trigger_random_event(game_state)
    
    session['game_state'] = game_state
    return jsonify({
        'game_state': game_state,
        'new_achievements': new_achievements,
        'new_event': new_event
    })

@app.route('/buy_upgrade/<upgrade_id>', methods=['POST'])
def buy_upgrade(upgrade_id):
    if 'game_state' not in session or upgrade_id not in UPGRADES:
        return jsonify({'error': 'Invalid upgrade'}), 400
    
    game_state = session['game_state']
    upgrade = UPGRADES[upgrade_id]
    current_level = game_state['upgrades'][upgrade_id]
    
    if current_level >= upgrade['max_level']:
        return jsonify({'error': 'Max level reached'}), 400
    
    # Calculate cost with increasing difficulty
    cost = upgrade['base_cost'] * (UPGRADE_MULTIPLIER ** current_level)
    
    if game_state['lines_of_code'] < cost:
        return jsonify({'error': 'Not enough lines of code'}), 400
    
    # Purchase successful
    game_state['lines_of_code'] -= cost
    game_state['upgrades'][upgrade_id] += 1
    game_state['stats']['upgrades_purchased'] += 1
    
    # Recalculate code per click
    game_state['code_per_click'] = CLICK_BASE_VALUE * game_state['prestige_multiplier']
    for u_id, level in game_state['upgrades'].items():
        game_state['code_per_click'] += UPGRADES[u_id]['click_bonus'] * level * game_state['prestige_multiplier']
    
    # Check for achievements
    new_achievements = check_achievements(game_state)
    
    # Check if this upgrade completes any active events
    event_completed = None
    for event in game_state['active_events']:
        if event['id'] == 'code_review' and not event['completed']:
            event['completed'] = True
            event_completed = event
            
            # Apply reward - temporary boost to production
            mult_id = f"event_boost_{datetime.now().timestamp()}"
            end_time = datetime.now().timestamp() + SPECIAL_EVENTS['code_review']['reward']['duration']
            
            if 'temporary_multipliers' not in game_state:
                game_state['temporary_multipliers'] = {}
            
            game_state['temporary_multipliers'][mult_id] = {
                'value': 1 + SPECIAL_EVENTS['code_review']['reward']['lines_bonus'],
                'end_time': end_time
            }
            break
    
    session['game_state'] = game_state
    return jsonify({
        'game_state': game_state,
        'new_achievements': new_achievements,
        'event_completed': event_completed
    })

@app.route('/buy_asset/<asset_id>', methods=['POST'])
def buy_asset(asset_id):
    if 'game_state' not in session or asset_id not in PASSIVE_ASSETS:
        return jsonify({'error': 'Invalid asset'}), 400
    
    game_state = session['game_state']
    asset = PASSIVE_ASSETS[asset_id]
    current_level = game_state['passive_assets'][asset_id]
    
    if current_level >= asset['max_level']:
        return jsonify({'error': 'Max level reached'}), 400
    
    # Calculate cost with increasing difficulty
    cost = asset['base_cost'] * (UPGRADE_MULTIPLIER ** current_level)
    
    if game_state['lines_of_code'] < cost:
        return jsonify({'error': 'Not enough lines of code'}), 400
    
    # Purchase successful
    game_state['lines_of_code'] -= cost
    game_state['passive_assets'][asset_id] += 1
    game_state['stats']['assets_purchased'] += 1
    
    # Recalculate passive income
    game_state['code_per_second'] = 0
    for a_id, level in game_state['passive_assets'].items():
        game_state['code_per_second'] += PASSIVE_ASSETS[a_id]['income'] * level * game_state['prestige_multiplier']
    
    # Update stats
    if game_state['code_per_second'] > game_state['stats']['highest_lines_per_second']:
        game_state['stats']['highest_lines_per_second'] = game_state['code_per_second']
    
    # Check for achievements
    new_achievements = check_achievements(game_state)
    
    session['game_state'] = game_state
    return jsonify({
        'game_state': game_state,
        'new_achievements': new_achievements
    })

@app.route('/prestige', methods=['POST'])
def prestige():
    if 'game_state' not in session:
        return jsonify({'error': 'No game state found'}), 400
    
    game_state = session['game_state']
    
    if game_state['lines_of_code'] < PRESTIGE_REQUIREMENT:
        return jsonify({'error': 'Not enough lines to prestige'}), 400
    
    # Calculate prestige bonus
    prestige_bonus = 1 + (game_state['lines_of_code'] / PRESTIGE_REQUIREMENT) * 0.1
    
    # Save some stats before reset
    old_prestige_level = game_state['prestige_level']
    old_achievements = game_state['achievements']
    old_stats = game_state['stats']
    old_stats['total_prestiges'] += 1
    
    # Reset game but keep prestige level and multiplier
    new_state = get_new_game_state()
    new_state['prestige_level'] = old_prestige_level + 1
    new_state['prestige_multiplier'] = game_state['prestige_multiplier'] + prestige_bonus
    new_state['code_per_click'] = CLICK_BASE_VALUE * new_state['prestige_multiplier']
    new_state['achievements'] = old_achievements
    new_state['stats'] = old_stats
    
    # Check for new achievements
    new_achievements = check_achievements(new_state)
    
    session['game_state'] = new_state
    return jsonify({
        'game_state': new_state,
        'new_achievements': new_achievements,
        'prestige_bonus': prestige_bonus
    })

@app.route('/complete_event/<event_id>', methods=['POST'])
def complete_event(event_id):
    if 'game_state' not in session:
        return jsonify({'error': 'No game state found'}), 400
    
    game_state = session['game_state']
    
    # Find the event
    event_completed = None
    for event in game_state['active_events']:
        if event['id'] == event_id and not event['completed']:
            event['completed'] = True
            event_completed = event
            
            # Apply event-specific rewards
            if event_id == 'bug_found':
                # Temporary click multiplier
                mult_id = f"event_boost_{datetime.now().timestamp()}"
                end_time = datetime.now().timestamp() + SPECIAL_EVENTS['bug_found']['reward']['duration']
                
                if 'temporary_multipliers' not in game_state:
                    game_state['temporary_multipliers'] = {}
                
                game_state['temporary_multipliers'][mult_id] = {
                    'value': SPECIAL_EVENTS['bug_found']['reward']['temporary_click_multiplier'],
                    'end_time': end_time
                }
            
            elif event_id == 'hackathon':
                # Check if the target was reached
                if game_state['lines_of_code'] >= event['target']:
                    # Unlock a special one-time upgrade
                    if 'hackathon_trophy' not in game_state.get('special_unlocks', []):
                        if 'special_unlocks' not in game_state:
                            game_state['special_unlocks'] = []
                        game_state['special_unlocks'].append('hackathon_trophy')
                        
                        # Add bonus lines
                        bonus = game_state['lines_of_code'] * 0.1  # 10% bonus
                        game_state['lines_of_code'] += bonus
            
            break
    
    # Remove completed events
    game_state['active_events'] = [e for e in game_state['active_events'] if not e['completed']]
    
    session['game_state'] = game_state
    return jsonify({
        'game_state': game_state,
        'event_completed': event_completed
    })

@app.route('/save', methods=['POST'])
def save_game():
    if 'game_state' not in session:
        return jsonify({'error': 'No game state to save'}), 400
    
    # In a real game, you might save to a database here
    return jsonify({'success': True, 'message': 'Game saved'})

@app.route('/reset', methods=['POST'])
def reset_game():
    session['game_state'] = get_new_game_state()
    return jsonify(session['game_state'])

@app.route('/stats', methods=['GET'])
def get_stats():
    if 'game_state' not in session:
        return jsonify({'error': 'No game state found'}), 400
    
    game_state = session['game_state']
    
    # Calculate some additional statistics
    stats = game_state['stats']
    stats['achievements_unlocked'] = len(game_state['achievements'])
    stats['achievements_total'] = len(ACHIEVEMENTS)
    stats['achievement_percentage'] = (stats['achievements_unlocked'] / stats['achievements_total']) * 100
    
    # Calculate efficiency metrics
    if stats.get('total_clicks', 0) > 0:
        stats['average_lines_per_click'] = stats['total_lines_from_clicks'] / stats['total_clicks']
    else:
        stats['average_lines_per_click'] = 0
    
    # Calculate time metrics
    total_playtime_seconds = game_state.get('longest_session', 0)
    hours = math.floor(total_playtime_seconds / 3600)
    minutes = math.floor((total_playtime_seconds % 3600) / 60)
    seconds = math.floor(total_playtime_seconds % 60)
    stats['total_playtime'] = f"{hours}h {minutes}m {seconds}s"
    
    return jsonify({
        'stats': stats,
        'prestige_level': game_state['prestige_level'],
        'prestige_multiplier': game_state['prestige_multiplier']
    })

@app.route('/update_lines', methods=['POST'])
def update_lines():
    """Update the server with the client's current lines of code (from passive income)"""
    if 'game_state' not in session:
        return jsonify({'error': 'No game state found'}), 400
    
    game_state = session['game_state']
    
    # Get current lines from client - using request.form instead of request.json
    client_lines = request.form.get('current_lines', type=float)
    client_last_tick = request.form.get('last_tick', type=float)
    
    # Use default values if parameters weren't provided
    if client_lines is None:
        client_lines = game_state['lines_of_code']
    if client_last_tick is None:
        client_last_tick = game_state['last_tick']
    
    # Update the server's record
    game_state['lines_of_code'] = client_lines
    game_state['last_tick'] = client_last_tick
    
    # Save to session
    session['game_state'] = game_state
    
    return jsonify({'success': True})

# Calculate the bulk purchase cost
def calculate_bulk_cost(base_cost, current_level, count, multiplier=UPGRADE_MULTIPLIER):
    total_cost = 0
    for i in range(count):
        level = current_level + i
        total_cost += base_cost * (multiplier ** level)
    return total_cost

# Add bulk buy endpoints
@app.route('/buy_upgrade_bulk/<upgrade_id>', methods=['POST'])
def buy_upgrade_bulk(upgrade_id):
    if 'game_state' not in session or upgrade_id not in UPGRADES:
        return jsonify({'error': 'Invalid upgrade'}), 400
    
    game_state = session['game_state']
    upgrade = UPGRADES[upgrade_id]
    current_level = game_state['upgrades'][upgrade_id]
    
    # Get the bulk buy amount
    count = int(request.form.get('count', 1))
    
    # Check if we're at max level
    if current_level >= upgrade['max_level']:
        return jsonify({'error': 'Max level reached'}), 400
    
    # Adjust count if it would exceed max level
    if current_level + count > upgrade['max_level']:
        count = upgrade['max_level'] - current_level
    
    # Calculate total cost
    total_cost = calculate_bulk_cost(upgrade['base_cost'], current_level, count)
    
    if game_state['lines_of_code'] < total_cost:
        return jsonify({'error': 'Not enough lines of code'}), 400
    
    # Purchase successful
    game_state['lines_of_code'] -= total_cost
    game_state['upgrades'][upgrade_id] += count
    game_state['stats']['upgrades_purchased'] += count
    
    # Recalculate code per click
    game_state['code_per_click'] = CLICK_BASE_VALUE * game_state['prestige_multiplier']
    for u_id, level in game_state['upgrades'].items():
        game_state['code_per_click'] += UPGRADES[u_id]['click_bonus'] * level * game_state['prestige_multiplier']
    
    # Check for achievements
    new_achievements = check_achievements(game_state)
    
    # Check for completed events
    event_completed = None
    for event in game_state['active_events']:
        if event['id'] == 'code_review' and not event['completed']:
            event['completed'] = True
            event_completed = event
            
            # Apply reward
            mult_id = f"event_boost_{datetime.now().timestamp()}"
            end_time = datetime.now().timestamp() + SPECIAL_EVENTS['code_review']['reward']['duration']
            
            if 'temporary_multipliers' not in game_state:
                game_state['temporary_multipliers'] = {}
            
            game_state['temporary_multipliers'][mult_id] = {
                'value': 1 + SPECIAL_EVENTS['code_review']['reward']['lines_bonus'],
                'end_time': end_time
            }
            break
    
    session['game_state'] = game_state
    return jsonify({
        'game_state': game_state,
        'new_achievements': new_achievements,
        'event_completed': event_completed
    })

@app.route('/buy_asset_bulk/<asset_id>', methods=['POST'])
def buy_asset_bulk(asset_id):
    if 'game_state' not in session or asset_id not in PASSIVE_ASSETS:
        return jsonify({'error': 'Invalid asset'}), 400
    
    game_state = session['game_state']
    asset = PASSIVE_ASSETS[asset_id]
    current_level = game_state['passive_assets'][asset_id]
    
    # Get the bulk buy amount
    count = int(request.form.get('count', 1))
    
    # Check if we're at max level
    if current_level >= asset['max_level']:
        return jsonify({'error': 'Max level reached'}), 400
    
    # Adjust count if it would exceed max level
    if current_level + count > asset['max_level']:
        count = asset['max_level'] - current_level
    
    # Calculate total cost
    total_cost = calculate_bulk_cost(asset['base_cost'], current_level, count)
    
    if game_state['lines_of_code'] < total_cost:
        return jsonify({'error': 'Not enough lines of code'}), 400
    
    # Purchase successful
    game_state['lines_of_code'] -= total_cost
    game_state['passive_assets'][asset_id] += count
    game_state['stats']['assets_purchased'] += count
    
    # Recalculate passive income
    game_state['code_per_second'] = 0
    for a_id, level in game_state['passive_assets'].items():
        game_state['code_per_second'] += PASSIVE_ASSETS[a_id]['income'] * level * game_state['prestige_multiplier']
    
    # Update stats
    if game_state['code_per_second'] > game_state['stats']['highest_lines_per_second']:
        game_state['stats']['highest_lines_per_second'] = game_state['code_per_second']
    
    # Check for achievements
    new_achievements = check_achievements(game_state)
    
    session['game_state'] = game_state
    return jsonify({
        'game_state': game_state,
        'new_achievements': new_achievements
    })

@app.route('/set_bulk_buy_mode', methods=['POST'])
def set_bulk_buy_mode():
    if 'game_state' not in session:
        return jsonify({'error': 'No game state found'}), 400
    
    game_state = session['game_state']
    
    # Get parameters
    type_key = request.form.get('type', 'upgrades')  # 'upgrades' or 'assets'
    mode = int(request.form.get('mode', 1))  # 1, 10, or 100
    
    # Validate inputs
    if type_key not in ['upgrades', 'assets']:
        return jsonify({'error': 'Invalid type'}), 400
    
    if mode not in [1, 10, 100]:
        return jsonify({'error': 'Invalid mode'}), 400
    
    # Initialize bulk_buy_mode if it doesn't exist
    if 'bulk_buy_mode' not in game_state:
        game_state['bulk_buy_mode'] = {'upgrades': 1, 'assets': 1}
    
    # Set the mode
    game_state['bulk_buy_mode'][type_key] = mode
    session['game_state'] = game_state
    
    return jsonify({'success': True, 'bulk_buy_mode': game_state['bulk_buy_mode']})

@app.route('/calculate_prestige_bonus', methods=['GET'])
def calculate_prestige_bonus():
    if 'game_state' not in session:
        return jsonify({'error': 'No game state found'}), 400
    
    game_state = session['game_state']
    current_lines = game_state['lines_of_code']
    
    # Calculate prestige bonus
    prestige_bonus = (current_lines / PRESTIGE_REQUIREMENT) * 0.1
    total_bonus = game_state['prestige_multiplier'] + prestige_bonus - 1
    
    return jsonify({
        'current_lines': current_lines,
        'prestige_requirement': PRESTIGE_REQUIREMENT,
        'prestige_bonus': prestige_bonus,
        'current_multiplier': game_state['prestige_multiplier'],
        'new_multiplier': game_state['prestige_multiplier'] + prestige_bonus,
        'total_bonus': total_bonus
    })

if __name__ == '__main__':
    app.run(debug=True)
