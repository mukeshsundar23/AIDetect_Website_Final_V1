document.addEventListener("DOMContentLoaded", function () {
  // Existing video detection code
  const videoForm = document.getElementById("videoForm");
  const videoInput = document.getElementById("videoInput");
  const videoPreview = document.getElementById("videoPreview");

  if (videoForm && videoInput && videoPreview) {
    console.log("✅ Video Detection JS Loaded");

    // Add toggle functionality for frame analysis
    const toggleFrameAnalysisBtn = document.getElementById("toggleFrameAnalysis");
    const frameAnalysisSection = document.getElementById("frameAnalysisSection");
    
    if (toggleFrameAnalysisBtn) {
      toggleFrameAnalysisBtn.addEventListener("click", function() {
        if (frameAnalysisSection.classList.contains("hidden")) {
          frameAnalysisSection.classList.remove("hidden");
          toggleFrameAnalysisBtn.innerHTML = '<i class="fas fa-chart-line mr-2"></i>Hide Frame-by-Frame Analysis';
        } else {
          frameAnalysisSection.classList.add("hidden");
          toggleFrameAnalysisBtn.innerHTML = '<i class="fas fa-chart-line mr-2"></i>View Frame-by-Frame Analysis';
        }
      });
    }

    videoInput.addEventListener("change", function () {
      console.log("📁 Video file selected");
      const file = this.files[0];
      if (file) {
        const preview = document.getElementById("videoPreview");
        preview.src = URL.createObjectURL(file);
        document.getElementById("videoPreviewContainer").classList.remove("hidden");
        console.log("🎞️ Preview loaded");
      }
    });

    videoForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      console.log("🔍 Form submitted!");

      const file = videoInput.files[0];
      if (!file) {
        alert("Please upload a video first.");
        console.warn("⚠️ No video file provided.");
        return;
      }

      // Hide any previous frame analysis sections
      if (frameAnalysisSection) {
        frameAnalysisSection.classList.add("hidden");
        if (toggleFrameAnalysisBtn) {
          toggleFrameAnalysisBtn.innerHTML = '<i class="fas fa-chart-line mr-2"></i>View Frame-by-Frame Analysis';
        }
      }

      document.getElementById("loading").classList.remove("hidden");
      document.getElementById("results").classList.add("hidden");

      let progress = 0;
      const progressBar = document.getElementById("progressBar");
      const progressText = document.getElementById("progressText");
      const interval = setInterval(() => {
        if (progress < 90) {
          progress += 10;
          progressBar.style.width = progress + "%";
          progressText.textContent = `Processing frame ${progress / 10} of 10`;
        }
      }, 200);

      const formData = new FormData();
      formData.append("file", file);
      console.log("📤 Sending request to backend...");

      try {
        const response = await fetch("http://localhost:8000/video-detect", {
          method: "POST",
          body: formData
        });

        clearInterval(interval);
        progressBar.style.width = "100%";
        progressText.textContent = `Processing complete`;

        const result = await response.json();
        console.log("✅ Result received:", result);

        document.getElementById("loading").classList.add("hidden");
        document.getElementById("results").classList.remove("hidden");

        const aiProb = result.final.label === "Fake" ? result.final.confidence : 1 - result.final.confidence;
        const humanProb = 1 - aiProb;

        document.getElementById("aiProbabilityBar").style.width = `${Math.round(aiProb * 100)}%`;
        document.getElementById("aiProbabilityText").innerText = `${Math.round(aiProb * 100)}% likely AI-generated`;

        document.getElementById("authenticProbabilityBar").style.width = `${Math.round(humanProb * 100)}%`;
        document.getElementById("authenticProbabilityText").innerText = `${Math.round(humanProb * 100)}% likely authentic`;

        const frameAnalysisContainer = document.getElementById("frameAnalysis");
        frameAnalysisContainer.innerHTML = ''; // Clear previous thumbnails

        // Create confidence chart
        if (result.frame_predictions && result.frame_predictions.length > 0) {
          // Prepare data for chart
          const frameNumbers = result.frame_predictions.map(frame => frame.frame);
          const confidenceValues = result.frame_predictions.map(frame => frame.confidence);
          const labels = result.frame_predictions.map(frame => frame.label);
          
          // Create chart
          const ctx = document.getElementById('confidenceChart').getContext('2d');
          new Chart(ctx, {
            type: 'line',
            data: {
              labels: frameNumbers,
              datasets: [{
                label: 'Confidence Score',
                data: confidenceValues,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1,
                fill: false
              }]
            },
            options: {
              responsive: true,
              scales: {
                y: {
                  beginAtZero: true,
                  max: 1,
                  title: {
                    display: true,
                    text: 'Confidence'
                  }
                },
                x: {
                  title: {
                    display: true,
                    text: 'Frame Number'
                  }
                }
              },
              plugins: {
                tooltip: {
                  callbacks: {
                    label: function(context) {
                      const frameIndex = context.dataIndex;
                      return `${labels[frameIndex]}: ${(confidenceValues[frameIndex] * 100).toFixed(2)}%`;
                    }
                  }
                }
              }
            }
          });
          
          // Add frame thumbnails
          result.frame_predictions.forEach((frame) => {
            const img = document.createElement("img");
            img.src = frame.thumbnail;
            img.alt = `Frame ${frame.frame}`;
            img.classList.add("rounded-lg", "shadow-sm", "w-full");

            const textContainer = document.createElement("div");
            textContainer.classList.add("text-center", "mt-2");

            const label = document.createElement("p");
            label.textContent = `Label: ${frame.label} - Confidence: ${(frame.confidence * 100).toFixed(2)}%`;
            label.classList.add("text-sm", "text-gray-600");

            textContainer.appendChild(label);
            frameAnalysisContainer.appendChild(img);
            frameAnalysisContainer.appendChild(textContainer);
          });
        } else {
          console.warn("⚠️ No frame predictions received.");
        }

      } catch (err) {
        clearInterval(interval);
        document.getElementById("loading").classList.add("hidden");
        console.error("❌ Error:", err);
        alert("Error: " + err.message);
      }
    });
  }

  // Text detection functionality
  const textForm = document.getElementById("textForm");
  
  if (textForm) {
    console.log("✅ Text Detection JS Loaded");
    
    textForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      console.log("🔍 Text form submitted!");
      
      const textInput = document.getElementById("textInput");
      const text = textInput.value.trim();
      
      if (!text) {
        alert("Please enter some text to analyze.");
        console.warn("⚠️ No text provided.");
        return;
      }
      
      document.getElementById("loading").classList.remove("hidden");
      document.getElementById("results").classList.add("hidden");
      
      try {
        const response = await fetch("http://localhost:8000/text-detect", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ 
            text: text,
            explain: true  // Request LIME explanations from backend
          })
        });
        
        const result = await response.json();
        console.log("✅ Text analysis result received:", result);
        
        document.getElementById("loading").classList.add("hidden");
        document.getElementById("results").classList.remove("hidden");
        
        // Determine if the text is AI-generated based on label or confidence
        let aiProb;
        if (result.label === "AI-generated") {
          aiProb = result.confidence !== undefined ? result.confidence : 0.8;
        } else if (result.label === "Human-written") {
          aiProb = result.confidence !== undefined ? 1 - result.confidence : 0.2;
        } else {
          // If no clear label, use confidence directly or default to 0.5
          aiProb = result.confidence !== undefined ? result.confidence : 0.5;
        }
        
        console.log("🧮 Calculated AI probability:", aiProb);
        
        // Ensure probabilities are between 0 and 1
        aiProb = Math.max(0, Math.min(1, aiProb));
        const humanProb = Math.max(0, Math.min(1, 1 - aiProb));
        
        // Format percentages as integers
        const aiPercent = Math.round(aiProb * 100);
        const humanPercent = Math.round(humanProb * 100);
        
        // Update UI - Check if elements exist before updating
        const aiProbabilityBar = document.getElementById("aiProbabilityBar");
        const aiProbabilityText = document.getElementById("aiProbabilityText");
        const humanProbabilityBar = document.getElementById("authenticProbabilityBar");
        const humanProbabilityText = document.getElementById("authenticProbabilityText");
        
        if (aiProbabilityBar) aiProbabilityBar.style.width = `${aiPercent}%`;
        if (aiProbabilityText) aiProbabilityText.innerText = `${aiPercent}% likely AI-generated`;
        
        if (humanProbabilityBar) humanProbabilityBar.style.width = `${humanPercent}%`;
        if (humanProbabilityText) humanProbabilityText.innerText = `${humanPercent}% likely authentic`;
        
        // Add key indicators
        const keyIndicators = document.getElementById("keyFindings");
        if (!keyIndicators) {
          console.warn("⚠️ keyFindings element not found");
          // Create the element if it doesn't exist
          const resultsDiv = document.getElementById("results");
          if (resultsDiv) {
            const indicatorsSection = document.createElement('div');
            indicatorsSection.innerHTML = `
              <h4 class="text-lg font-semibold mb-2">Key Findings</h4>
              <ul id="keyFindings" class="list-disc pl-5 space-y-1"></ul>
            `;
            resultsDiv.appendChild(indicatorsSection);
          }
        }
        
        // Try to get the keyIndicators element again in case it was just created
        const keyIndicatorsElement = document.getElementById("keyFindings");
        if (keyIndicatorsElement) {
          keyIndicatorsElement.innerHTML = '';
          
          // Display explanations if available
          if (result.lime_explanations && Array.isArray(result.lime_explanations)) {
            result.lime_explanations.forEach(explanation => {
              keyIndicatorsElement.innerHTML += `<li>${explanation}</li>`;
            });
            
            // If we have a heatmap image, display it
            if (result.heatmap_image) {
              const heatmapContainer = document.createElement('div');
              heatmapContainer.classList.add('mt-6');
              heatmapContainer.innerHTML = `
                <h4 class="text-lg font-semibold mb-2">Explanation Heatmap</h4>
                <div class="flex space-x-4">
                  <div class="w-1/2">
                    <p class="text-sm text-gray-600 mb-2">Original Image</p>
                    <img src="${result.image || URL.createObjectURL(file)}" class="rounded-lg shadow-sm w-full" alt="Original image">
                  </div>
                  <div class="w-1/2">
                    <p class="text-sm text-gray-600 mb-2">Areas influencing prediction</p>
                    <img src="${result.heatmap_image}" class="rounded-lg shadow-sm w-full" alt="Explanation heatmap">
                  </div>
                </div>
              `;
              document.getElementById("results").appendChild(heatmapContainer);
            }
          } else {
            // Fallback to generic explanations
            const indicators = [
              `${result.label} detected with ${Math.round(result.confidence * 100)}% confidence`,
              "Check for unnatural artifacts or inconsistencies",
              "Look for unusual lighting or shadows",
              "Examine edges of objects for blurring or artifacts"
            ];
            
            indicators.forEach(indicator => {
              keyIndicatorsElement.innerHTML += `<li>${indicator}</li>`;
            });
          }
        }
      } catch (err) {
        document.getElementById("loading").classList.add("hidden");
        console.error("❌ Error:", err);
        alert("Error analyzing text: " + err.message);
      }
    });
  }
  
  // Explainability function to generate more meaningful indicators
  function generateExplainableIndicators(text, aiProbability) {
    const indicators = [];
    
    // Text statistics
    const wordCount = text.split(/\s+/).length;
    const sentenceCount = text.split(/[.!?]+/).filter(Boolean).length;
    const avgWordsPerSentence = wordCount / Math.max(1, sentenceCount);
    
    // Check for repetition
    const words = text.toLowerCase().match(/\b\w+\b/g) || [];
    const wordFrequency = {};
    words.forEach(word => {
      if (word.length > 3) { // Only count words longer than 3 letters
        wordFrequency[word] = (wordFrequency[word] || 0) + 1;
      }
    });
    
    // Find repeated phrases (3+ words)
    const repeatedPhrases = findRepeatedPhrases(text);
    
    // Generate indicators based on AI probability and text analysis
    if (aiProbability > 0.7) {
      indicators.push("High confidence in AI-generated content detection");
      
      if (avgWordsPerSentence > 20) {
        indicators.push("Unusually consistent sentence length (avg: " + avgWordsPerSentence.toFixed(1) + " words)");
      }
      
      if (repeatedPhrases.length > 0) {
        indicators.push("Detected repeated phrases or patterns");
      }
      
      // Check for common AI writing patterns
      if (text.includes("In conclusion") || text.includes("To summarize")) {
        indicators.push("Uses formulaic transition phrases common in AI writing");
      }
      
      indicators.push("Limited stylistic variations typical of AI generation");
    } 
    else if (aiProbability > 0.4) {
      indicators.push("Mixed indicators detected (moderate confidence)");
      
      if (repeatedPhrases.length > 0) {
        indicators.push("Some repetitive patterns detected");
      } else {
        indicators.push("Few repetitive patterns detected");
      }
      
      indicators.push("Balanced mix of formulaic and varied expressions");
      
      if (avgWordsPerSentence > 15 && avgWordsPerSentence < 20) {
        indicators.push("Moderately consistent sentence structure");
      }
    } 
    else {
      indicators.push("Strong indicators of human-written content");
      
      if (avgWordsPerSentence < 15 || avgWordsPerSentence > 25) {
        indicators.push("Natural variation in sentence length");
      }
      
      if (repeatedPhrases.length === 0) {
        indicators.push("No significant repetitive patterns detected");
      }
      
      // Look for human writing indicators
      if (text.includes("I") || text.includes("my") || text.includes("we")) {
        indicators.push("Personal perspective indicators present");
      }
      
      indicators.push("Organic flow and natural language transitions");
    }
    
    return indicators;
  }
  
  // Helper function to find repeated phrases
  function findRepeatedPhrases(text) {
    const phrases = [];
    const words = text.toLowerCase().match(/\b\w+\b/g) || [];
    
    // Look for 3-word phrases that repeat
    for (let i = 0; i < words.length - 3; i++) {
      const phrase = words.slice(i, i + 3).join(" ");
      const restOfText = words.slice(i + 3).join(" ");
      
      if (restOfText.includes(phrase)) {
        phrases.push(phrase);
      }
    }
    
    // Return unique phrases
    return [...new Set(phrases)];
  }
});

// Image detection functionality
  const imageForm = document.getElementById("imageForm");
  
  if (imageForm) {
    console.log("✅ Image Detection JS Loaded");
    
    const imageInput = document.getElementById("imageInput");
    const imagePreview = document.getElementById("imagePreview");
    
    imageInput.addEventListener("change", function() {
      const file = this.files[0];
      if (file) {
        imagePreview.src = URL.createObjectURL(file);
        document.getElementById("imagePreviewContainer").classList.remove("hidden");
        console.log("🖼️ Image preview loaded");
      }
    });
    
    imageForm.addEventListener("submit", async function(e) {
      e.preventDefault();
      console.log("🔍 Image form submitted!");
      
      const file = imageInput.files[0];
      if (!file) {
        alert("Please upload an image first.");
        console.warn("⚠️ No image file provided.");
        return;
      }
      
      document.getElementById("loading").classList.remove("hidden");
      document.getElementById("results").classList.add("hidden");
      
      const formData = new FormData();
      formData.append("file", file);
      
      try {
        const response = await fetch("http://localhost:8000/image-detect", {
          method: "POST",
          body: formData
        });
        
        const result = await response.json();
        console.log("✅ Image analysis result received:", result);
        
        document.getElementById("loading").classList.add("hidden");
        document.getElementById("results").classList.remove("hidden");
        
        // Determine if the image is AI-generated based on label or confidence
        let aiProb;
        if (result.label === "AI-generated") {
          aiProb = result.confidence !== undefined ? result.confidence : 0.8;
        } else if (result.label === "Real") {
          aiProb = result.confidence !== undefined ? 1 - result.confidence : 0.2;
        } else {
          aiProb = result.confidence !== undefined ? result.confidence : 0.5;
        }
        
        console.log("🧮 Calculated AI probability:", aiProb);
        
        // Ensure probabilities are between 0 and 1
        aiProb = Math.max(0, Math.min(1, aiProb));
        const humanProb = Math.max(0, Math.min(1, 1 - aiProb));
        
        // Format percentages as integers
        const aiPercent = Math.round(aiProb * 100);
        const humanPercent = Math.round(humanProb * 100);
        
        // Update UI - Check if elements exist before updating
        const aiProbabilityBar = document.getElementById("aiProbabilityBar");
        const aiProbabilityText = document.getElementById("aiProbabilityText");
        const humanProbabilityBar = document.getElementById("authenticProbabilityBar");
        const humanProbabilityText = document.getElementById("authenticProbabilityText");
        
        if (aiProbabilityBar) aiProbabilityBar.style.width = `${aiPercent}%`;
        if (aiProbabilityText) aiProbabilityText.innerText = `${aiPercent}% likely AI-generated`;
        
        if (humanProbabilityBar) humanProbabilityBar.style.width = `${humanPercent}%`;
        if (humanProbabilityText) humanProbabilityText.innerText = `${humanPercent}% likely authentic`;
        
        // Add key indicators
        const keyIndicators = document.getElementById("keyIndicators");
        if (!keyIndicators) {
          console.warn("⚠️ keyIndicators element not found");
          // Create the element if it doesn't exist
          const resultsDiv = document.getElementById("results");
          if (resultsDiv) {
            const indicatorsSection = document.createElement('div');
            indicatorsSection.innerHTML = `
              <h4 class="text-lg font-semibold mb-2">Key Indicators</h4>
              <ul id="keyIndicators" class="list-disc pl-5 space-y-1"></ul>
            `;
            resultsDiv.appendChild(indicatorsSection);
          }
        }
        
        // Try to get the keyIndicators element again in case it was just created
        const keyIndicatorsElement = document.getElementById("keyIndicators");
        if (keyIndicatorsElement) {
          keyIndicatorsElement.innerHTML = '';
          
          // Display explanations if available
          if (result.lime_explanations && Array.isArray(result.lime_explanations)) {
            result.lime_explanations.forEach(explanation => {
              keyIndicatorsElement.innerHTML += `<li>${explanation}</li>`;
            });
            
            // If we have a heatmap image, display it
            if (result.heatmap_image) {
              const heatmapContainer = document.createElement('div');
              heatmapContainer.classList.add('mt-6');
              heatmapContainer.innerHTML = `
                <h4 class="text-lg font-semibold mb-2">Explanation Heatmap</h4>
                <div class="flex space-x-4">
                  <div class="w-1/2">
                    <p class="text-sm text-gray-600 mb-2">Original Image</p>
                    <img src="${result.image || URL.createObjectURL(file)}" class="rounded-lg shadow-sm w-full" alt="Original image">
                  </div>
                  <div class="w-1/2">
                    <p class="text-sm text-gray-600 mb-2">Areas influencing prediction</p>
                    <img src="${result.heatmap_image}" class="rounded-lg shadow-sm w-full" alt="Explanation heatmap">
                  </div>
                </div>
              `;
              document.getElementById("results").appendChild(heatmapContainer);
            }
          } else {
            // Fallback to generic explanations
            const indicators = [
              `${result.label} detected with ${Math.round(result.confidence * 100)}% confidence`,
              "Check for unnatural artifacts or inconsistencies",
              "Look for unusual lighting or shadows",
              "Examine edges of objects for blurring or artifacts"
            ];
            
            indicators.forEach(indicator => {
              keyIndicators.innerHTML += `<li>${indicator}</li>`;
            });
          }
        }
      } catch (err) {
        document.getElementById("loading").classList.add("hidden");
        console.error("❌ Error:", err);
        alert("Error analyzing image: " + err.message);
      }
    });
  }