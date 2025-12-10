#!/usr/bin/env node

/**
 * Export Excalidraw diagram to PNG
 *
 * This script uses Puppeteer to render the Excalidraw diagram in a headless browser
 * and export it as a PNG image at high resolution.
 *
 * Requirements:
 *     npm install puppeteer
 */

const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

const EXCALIDRAW_FILE = path.join(__dirname, 'jpspec-workflow.excalidraw');
const OUTPUT_PNG = path.join(__dirname, 'jpspec-workflow.png');
const WIDTH = 1920;
const SCALE = 2; // For high DPI

async function exportToPng() {
  console.log('Loading Excalidraw diagram...');
  const excalidrawData = JSON.parse(fs.readFileSync(EXCALIDRAW_FILE, 'utf8'));

  console.log('Launching browser...');
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  try {
    const page = await browser.newPage();

    // Set viewport to desired width
    await page.setViewport({
      width: WIDTH,
      height: 1200,
      deviceScaleFactor: SCALE
    });

    // Create HTML with embedded Excalidraw viewer
    const html = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {
      margin: 0;
      padding: 20px;
      background: white;
    }
    #canvas {
      width: 100%;
      height: 100%;
    }
  </style>
</head>
<body>
  <canvas id="canvas"></canvas>
  <script type="module">
    const excalidrawData = ${JSON.stringify(excalidrawData)};

    // Simple canvas renderer for Excalidraw elements
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');

    // Calculate bounds
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    excalidrawData.elements.forEach(el => {
      minX = Math.min(minX, el.x);
      minY = Math.min(minY, el.y);
      maxX = Math.max(maxX, el.x + (el.width || 0));
      maxY = Math.max(maxY, el.y + (el.height || 0));
    });

    const padding = 50;
    const width = maxX - minX + padding * 2;
    const height = maxY - minY + padding * 2;

    canvas.width = width * ${SCALE};
    canvas.height = height * ${SCALE};
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';

    ctx.scale(${SCALE}, ${SCALE});
    ctx.translate(-minX + padding, -minY + padding);

    // Render elements
    excalidrawData.elements.forEach(el => {
      ctx.save();

      // Set styles
      ctx.strokeStyle = el.strokeColor || '#000';
      ctx.fillStyle = el.backgroundColor || 'transparent';
      ctx.lineWidth = el.strokeWidth || 1;
      ctx.globalAlpha = (el.opacity || 100) / 100;

      if (el.strokeStyle === 'dashed') {
        ctx.setLineDash([5, 5]);
      }

      if (el.type === 'rectangle') {
        const radius = el.roundness?.type === 3 ? 8 : 0;
        if (radius > 0) {
          // Rounded rectangle
          ctx.beginPath();
          ctx.moveTo(el.x + radius, el.y);
          ctx.lineTo(el.x + el.width - radius, el.y);
          ctx.quadraticCurveTo(el.x + el.width, el.y, el.x + el.width, el.y + radius);
          ctx.lineTo(el.x + el.width, el.y + el.height - radius);
          ctx.quadraticCurveTo(el.x + el.width, el.y + el.height, el.x + el.width - radius, el.y + el.height);
          ctx.lineTo(el.x + radius, el.y + el.height);
          ctx.quadraticCurveTo(el.x, el.y + el.height, el.x, el.y + el.height - radius);
          ctx.lineTo(el.x, el.y + radius);
          ctx.quadraticCurveTo(el.x, el.y, el.x + radius, el.y);
          ctx.closePath();
        } else {
          ctx.beginPath();
          ctx.rect(el.x, el.y, el.width, el.height);
          ctx.closePath();
        }

        if (el.backgroundColor !== 'transparent') {
          ctx.fill();
        }
        ctx.stroke();
      } else if (el.type === 'diamond') {
        ctx.beginPath();
        const cx = el.x + el.width / 2;
        const cy = el.y + el.height / 2;
        ctx.moveTo(cx, el.y);
        ctx.lineTo(el.x + el.width, cy);
        ctx.lineTo(cx, el.y + el.height);
        ctx.lineTo(el.x, cy);
        ctx.closePath();

        if (el.backgroundColor !== 'transparent') {
          ctx.fill();
        }
        ctx.stroke();
      } else if (el.type === 'arrow') {
        const points = el.points;
        if (points && points.length > 0) {
          ctx.beginPath();
          ctx.moveTo(el.x + points[0][0], el.y + points[0][1]);
          for (let i = 1; i < points.length; i++) {
            ctx.lineTo(el.x + points[i][0], el.y + points[i][1]);
          }
          ctx.stroke();

          // Draw arrowhead
          if (el.endArrowhead === 'arrow' && points.length > 1) {
            const lastPoint = points[points.length - 1];
            const prevPoint = points[points.length - 2];
            const angle = Math.atan2(lastPoint[1] - prevPoint[1], lastPoint[0] - prevPoint[0]);
            const arrowSize = 10;

            ctx.beginPath();
            ctx.moveTo(el.x + lastPoint[0], el.y + lastPoint[1]);
            ctx.lineTo(
              el.x + lastPoint[0] - arrowSize * Math.cos(angle - Math.PI / 6),
              el.y + lastPoint[1] - arrowSize * Math.sin(angle - Math.PI / 6)
            );
            ctx.moveTo(el.x + lastPoint[0], el.y + lastPoint[1]);
            ctx.lineTo(
              el.x + lastPoint[0] - arrowSize * Math.cos(angle + Math.PI / 6),
              el.y + lastPoint[1] - arrowSize * Math.sin(angle + Math.PI / 6)
            );
            ctx.stroke();
          }
        }
      } else if (el.type === 'text') {
        ctx.font = \`\${el.fontSize || 16}px Arial\`;
        ctx.fillStyle = el.strokeColor || '#000';
        ctx.textAlign = el.textAlign || 'left';
        ctx.textBaseline = el.verticalAlign || 'top';

        const lines = el.text.split('\\n');
        const lineHeight = (el.fontSize || 16) * (el.lineHeight || 1.25);

        lines.forEach((line, i) => {
          let x = el.x;
          if (el.textAlign === 'center') {
            x += el.width / 2;
          } else if (el.textAlign === 'right') {
            x += el.width;
          }

          ctx.fillText(line, x, el.y + i * lineHeight);
        });
      }

      ctx.restore();
    });

    // Signal completion
    window.renderComplete = true;
  </script>
</body>
</html>
    `;

    await page.setContent(html);

    // Wait for render to complete
    await page.waitForFunction(() => window.renderComplete, { timeout: 10000 });

    // Add small delay for final render
    await new Promise(resolve => setTimeout(resolve, 1000));

    console.log('Taking screenshot...');
    const canvas = await page.$('#canvas');
    await canvas.screenshot({
      path: OUTPUT_PNG,
      omitBackground: false
    });

    console.log(`✓ PNG exported to: ${OUTPUT_PNG}`);
    console.log(`  Dimensions: ${WIDTH}px width (${SCALE}x scale)`);

  } finally {
    await browser.close();
  }
}

// Run export
exportToPng().catch(err => {
  console.error('Export failed:', err);
  process.exit(1);
});
