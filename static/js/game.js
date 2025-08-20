// Game utilities and helper functions

/**
 * Format large numbers to be more readable
 * @param {number} num - The number to format
 * @returns {string} Formatted number
 */
function formatNumber(num) {
    if (num >= 1000000000) {
        return (num / 1000000000).toFixed(2) + 'B';
    } else if (num >= 1000000) {
        return (num / 1000000).toFixed(2) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(2) + 'K';
    } else {
        return Math.floor(num);
    }
}

/**
 * Create floating code particles
 * @param {number} x - X coordinate
 * @param {number} y - Y coordinate
 */
function createCodeParticle(x, y) {
    const particles = $('#particles-container');
    const codeSymbols = ['{ }', '( )', '[ ]', ';', '==', '+=', '=>', '&&', '||', '//', '++', '--'];
    const symbol = codeSymbols[Math.floor(Math.random() * codeSymbols.length)];
    
    const particle = $(`<div class="code-particle">${symbol}</div>`);
    particle.css({
        left: x,
        top: y,
        position: 'absolute',
        opacity: 1,
        fontSize: '16px',
        pointerEvents: 'none',
        zIndex: 9999
    });
    
    particles.append(particle);
    
    // Random initial velocity
    const angle = Math.random() * Math.PI * 2;
    const speed = 2 + Math.random() * 4;
    const vx = Math.cos(angle) * speed;
    const vy = -5 - Math.random() * 5; // Always go up initially
    
    let posX = x;
    let posY = y;
    let opacity = 1;
    const lifetime = 50 + Math.random() * 50;
    let age = 0;
    
    function updateParticle() {
        if (age >= lifetime) {
            particle.remove();
            return;
        }
        
        posX += vx;
        posY += vy;
        opacity -= 1 / lifetime;
        
        particle.css({
            left: posX,
            top: posY,
            opacity: opacity
        });
        
        age++;
        requestAnimationFrame(updateParticle);
    }
    
    updateParticle();
}

/**
 * Generate a random programming code snippet
 * @returns {string} A random code snippet
 */
function getRandomCodeSnippet() {
    const snippets = [
        'console.log("Hello, World!");',
        'function calculateSum(a, b) { return a + b; }',
        'const items = [1, 2, 3].map(x => x * 2);',
        'if (condition) { doSomething(); } else { doSomethingElse(); }',
        'class User { constructor(name) { this.name = name; } }',
        'try { riskyOperation(); } catch (error) { handleError(error); }',
        'import { Component } from "@framework/core";',
        'const API_URL = process.env.API_URL || "https://api.example.com";',
        'document.getElementById("app").addEventListener("click", handleClick);',
        'const result = await fetch("/api/data").then(res => res.json());',
        'export default function App() { return <div>Hello World</div>; }',
        'const serverless = require("serverless-http");',
        'git commit -m "Fix critical bug in production"',
        'docker-compose up -d',
        'npm install --save-dev typescript @types/node',
        'SELECT * FROM users WHERE active = true LIMIT 100;',
        'CREATE INDEX idx_user_email ON users(email);',
        'public static void main(String[] args) {',
        'plt.figure(figsize=(10, 6))',
        'const train_loader = DataLoader(train_dataset, batch_size=32)',
        'kubectl apply -f deployment.yaml',
        '@app.route("/api/users", methods=["GET"])',
        'terraform init && terraform apply',
        'async function fetchData() { return await api.get("/data"); }',
        'for (let i = 0; i < array.length; i++) { sum += array[i]; }',
        'const [state, setState] = useState(initialValue);',
        'useEffect(() => { fetchData(); }, []);',
        'switch (value) { case 1: return "One"; default: return "Other"; }',
        'def calculate_average(numbers): return sum(numbers) / len(numbers)',
        '@dataclass class Point: x: float; y: float',
        'const memoizedValue = useMemo(() => computeExpensiveValue(a, b), [a, b]);'
    ];
    
    return snippets[Math.floor(Math.random() * snippets.length)];
}

/**
 * Show a notification popup
 * @param {string} title - Notification title
 * @param {string} message - Notification message
 */
function showNotification(title, message) {
    $('#achievement-text').text(`${title}: ${message}`);
    $('#achievement-popup').addClass('show');
    setTimeout(() => {
        $('#achievement-popup').removeClass('show');
    }, 3000);
}

/**
 * Display a sequence of achievement notifications
 * @param {Array} achievements - List of achievement IDs
 */
function showNewAchievements(achievements) {
    if (!achievements || achievements.length === 0) return;
    
    let index = 0;
    
    function showNext() {
        if (index >= achievements.length) return;
        
        const achievementId = achievements[index];
        const achievement = ACHIEVEMENTS[achievementId];
        
        if (achievement) {
            showNotification('Achievement Unlocked', `${achievement.name}: ${achievement.description}`);
            
            if (achievement.reward) {
                let rewardText = '';
                if (achievement.reward.click_bonus) rewardText = `+${achievement.reward.click_bonus} lines per click`;
                else if (achievement.reward.click_multiplier) rewardText = `${achievement.reward.click_multiplier}x click power`;
                else if (achievement.reward.passive_bonus) rewardText = `+${achievement.reward.passive_bonus} lines per second`;
                else if (achievement.reward.passive_multiplier) rewardText = `${achievement.reward.passive_multiplier}x passive income`;
                else if (achievement.reward.prestige_bonus) rewardText = `+${achievement.reward.prestige_bonus} prestige multiplier`;
                
                if (rewardText) {
                    setTimeout(() => {
                        showNotification('Achievement Reward', rewardText);
                    }, 3500);
                }
            }
        }
        
        index++;
        setTimeout(showNext, 4000);
    }
    
    showNext();
}

/**
 * Applying special visual effects based on game theme and progress
 */
function applySpecialEffects() {
    // Apply special effects based on current theme
    if (gameState.theme === 'holographic.css') {
        // Special holographic effects
        if (!window.holographicEffectsApplied) {
            // Add floating background elements
            for (let i = 0; i < 10; i++) {
                const size = 5 + Math.random() * 15;
                const element = $('<div class="holo-particle"></div>');
                element.css({
                    width: size + 'px',
                    height: size + 'px',
                    left: Math.random() * 100 + '%',
                    top: Math.random() * 100 + '%',
                    animationDuration: (5 + Math.random() * 10) + 's',
                    animationDelay: (Math.random() * 5) + 's'
                });
                $('body').append(element);
            }
            
            window.holographicEffectsApplied = true;
        }
    } else {
        // Remove holographic effects if theme changed
        if (window.holographicEffectsApplied) {
            $('.holo-particle').remove();
            window.holographicEffectsApplied = false;
        }
    }
}

// Export functions for use in the main script
window.GameUtils = {
    formatNumber,
    createCodeParticle,
    getRandomCodeSnippet,
    showNotification,
    showNewAchievements,
    applySpecialEffects
};
