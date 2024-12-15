let players = [];

document.addEventListener("DOMContentLoaded", function () {
    const container = document.getElementById("bar-container");

    // get data from data attributes
    const player1Stats = JSON.parse(container.getAttribute("data-player1-stats"));
    const player2Stats = JSON.parse(container.getAttribute("data-player2-stats"));

    players = [container.getAttribute("data-player1-name"), 
        container.getAttribute("data-player2-name")];

    const playerStats = {
        "Points": [player1Stats.PTS, player2Stats.PTS],
        "Rebounds": [player1Stats.TRB, player2Stats.TRB],
        "Assists": [player1Stats.AST, player2Stats.AST],
        "Blocks": [player1Stats.BLK, player2Stats.BLK],
        "Steals": [player1Stats.STL, player2Stats.STL],
        "FG%": [player1Stats['FG%'], player2Stats['FG%']],

    };

    const playerColors = ["#133f79", "#009879"];

    // create the legend section
    function createLegend() {
        const legendContainer = document.createElement("div");
        legendContainer.className = "legend-container";

        for (let i = 0; i < players.length; i++) {
            const legendItem = document.createElement("div");
            legendItem.className = "legend-item";

            // create the colored box
            const colorBox = document.createElement("div");
            colorBox.className = "color-box";
            colorBox.style.backgroundColor = playerColors[i];

            // create the player label
            const playerLabel = document.createElement("div");
            playerLabel.className = "player-label";
            playerLabel.innerText = players[i];

            legendItem.appendChild(colorBox);
            legendItem.appendChild(playerLabel);
            legendContainer.appendChild(legendItem);
        }

        container.insertBefore(legendContainer, container.firstChild);  // Insert the legend at the top
    }

    // function to create the bar sections
    function createBarSection(statName, values) {
        const maxValue = Math.max(...values);

        const section = document.createElement("div");
        section.className = "bar-section";

        const statRow = document.createElement("div");
        statRow.className = "stat-row";

        // stat name (only once)
        const statLabel = document.createElement("div");
        statLabel.className = "bar-stat";
        statLabel.innerText = statName;

        // player names and values column (middle column)
        const playerValuesContainer = document.createElement("div");
        playerValuesContainer.className = "player-values-container";

        // bar visual container (right column)
        const barVisualContainer = document.createElement("div");
        barVisualContainer.className = "bar-visual-container";

        // add player names and values + bars to the row
        for (let i = 0; i < values.length; i++) {
            const playerValue = document.createElement("div");
            playerValue.className = "player-value";
            playerValue.innerText = `${values[i]}`;

            const barVisual = document.createElement("div");
            barVisual.className = "bar-visual";
            barVisual.style.width = `${(values[i] / maxValue) * 100}%`;
            barVisual.style.backgroundColor = playerColors[i];  // Set the color based on the player

            const barContainer = document.createElement("div");
            barContainer.className = "bar-container";
            barContainer.appendChild(barVisual);

            // append player data (name + value) and bar visual
            playerValuesContainer.appendChild(playerValue);
            barVisualContainer.appendChild(barContainer);
        }

        statRow.appendChild(statLabel);
        statRow.appendChild(playerValuesContainer);
        statRow.appendChild(barVisualContainer);
        section.appendChild(statRow);
        container.appendChild(section);
    }

    // create the legend at the top of the container
    createLegend();

    // generate bars for each stat
    for (const [statName, values] of Object.entries(playerStats)) {
        createBarSection(statName, values);
    }
});

document.addEventListener("DOMContentLoaded", function () {
    // modal functionality
    const modal = document.getElementById("infoModal");
    const infoText = document.getElementById("infoText");
    const closeBtn = document.getElementsByClassName("close-btn")[0];

    infoText.onclick = function() {
        modal.style.display = "block";
    };

    closeBtn.onclick = function() {
        modal.style.display = "none";
    };

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    };
});

// download the comparison chart
document.addEventListener("DOMContentLoaded", function () {
    document.getElementById('download').addEventListener('click', () => {
        console.log('clicked')

        const header = document.getElementsByClassName('heading')[1];
        const originalBorderRadius = window.getComputedStyle(header).borderRadius;

        const title = players[0].replace(/\s+/g, '') + 'Vs' + players[1].replace(/\s+/g, '');
        
        header.style.setProperty('border-radius', '0');
        html2canvas(document.getElementById('chart')).then((canvas) => {
          header.style.borderRadius = originalBorderRadius;
          const link = document.createElement('a');
          link.download = title + '.png';
          link.href = canvas.toDataURL();
          link.click();
        });
      });
});

  