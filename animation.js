(() => {
  'use strict';

  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');
  const W = 480, H = 270;
  canvas.width = W;
  canvas.height = H;

  // ── Timing（动画结束后即转场，TRANS_DUR = 0.5s）──
  const TRANS_DUR = 0.5;
  const SCENE1_END = 5;
  const TRANS1_END = SCENE1_END + TRANS_DUR;
  const SCENE2_END = TRANS1_END + 4.5;
  const TRANS2_END = SCENE2_END + TRANS_DUR;
  const SCENE3_END = TRANS2_END + 7;
  const TRANS3_END = SCENE3_END + TRANS_DUR;
  const SCENE4_END = TRANS3_END + 5;
  const TRANS4_END = SCENE4_END + TRANS_DUR;
  const SCENE5_END = TRANS4_END + 7;
  const TRANS5_END = SCENE5_END + TRANS_DUR;
  const SCENE6_END = TRANS5_END + 5;
  const TRANS6_END = SCENE6_END + TRANS_DUR;
  const SCENE7_END = TRANS6_END + 8;
  const FADE_END = SCENE7_END + TRANS_DUR;
  const TOTAL = FADE_END;
  const SCENE7_DUR = SCENE7_END - TRANS6_END;
  const SCENE7_BAR_HOLD = 0.5;
  let startTs = null;

  // ── Color Palette ──
  const C = {
    wall:       '#f2f4f8',
    wallLine:   '#e2e6ee',
    floor:      '#e8eaef',
    floorLine:  '#d8dce4',
    shelf:      '#6a5a4a',
    bookR:      '#c0392b', bookB: '#2980b9', bookG: '#27ae60',
    bookY:      '#f39c12', bookP: '#8e44ad',
    desk:       '#8B6914',
    deskTop:    '#a07828',
    deskLeg:    '#6a5010',
    chair:      '#5a4a3a',
    chairSeat:  '#7a6a5a',
    monFrame:   '#c8c8c8',
    monScreen:  '#f0faf0',
    monText:    '#1a8a3a',
    winFrame:   '#c8ccd8',
    winGlass:   '#d8e8f8',
    winLight:   '#b8d4f0',
    skin:       '#ffd5a0',
    skinShade:  '#e8b880',
    hair:       '#3d2b1f',
    eye:        '#222222',
    whiteCoat:  '#e8e8e8',
    coatShade:  '#cccccc',
    pants:      '#3d3d5c',
    shoes:      '#2a2a2a',
    grayHair:   '#888888',
    gown:       '#87ceeb',
    gownShade:  '#6aadcc',
    shirt:      '#e07050',
    shirtShade: '#c05535',
    jeans:      '#4a6fa5',
    jeansShade: '#3a5a88',
    darkHair:   '#2a1a0a',
    bubbleBg:   '#ffffff',
    bubbleBdr:  '#aaaaaa',
    bubbleTxt:  '#333333',
    divider:    '#d0d4dc',
    dividerHi:  '#e8eaef',
    labelGrn:   '#1a9a5c',
    labelOrg:   '#d07020',
    panelLeft:  '#f0f6fc',
    panelRight: '#fff6f0',
    sceneBg:    '#ffffff',
    robotBody:  '#c8d0d8',
    robotLight: '#e4eaf0',
    robotDark:  '#98a4b0',
    robotAccent:'#1a9a5c',
    robotEye:   '#2ecc71',
    coatGreen:  '#5cb85c',
    coatGrnSh:  '#449d44',
    coatBlue:   '#5b9bd5',
    coatBluSh:  '#3a7fc4',
    barHumanSP: '#a8d4f0',
    barEasyMED: '#b8e8b0',
  };

  // ── Utilities ──

  function fill(x, y, w, h, c) {
    ctx.fillStyle = c;
    ctx.fillRect(Math.floor(x), Math.floor(y), Math.ceil(w), Math.ceil(h));
  }

  const FONT = '"PingFang SC","Hiragino Sans GB","Microsoft YaHei","WenQuanYi Micro Hei",monospace';

  function txt(str, x, y, c, sz, al) {
    ctx.fillStyle = c;
    ctx.font = 'bold ' + sz + 'px ' + FONT;
    ctx.textAlign = al || 'left';
    ctx.textBaseline = 'top';
    ctx.fillText(str, Math.floor(x), Math.floor(y));
  }

  function typewrite(str, x, y, c, sz, t, spd, al) {
    const n = Math.min(Math.floor(t * (spd || 8)), str.length);
    if (n <= 0) return false;
    txt(str.substring(0, n), x, y, c, sz, al);
    return n >= str.length;
  }

  function drawBubble(bx, by, bw, bh, tailX, tailDir) {
    ctx.fillStyle = C.bubbleBg;
    ctx.strokeStyle = C.bubbleBdr;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(bx + 2, by);
    ctx.lineTo(bx + bw - 2, by);
    ctx.lineTo(bx + bw, by + 2);
    ctx.lineTo(bx + bw, by + bh - 2);
    ctx.lineTo(bx + bw - 2, by + bh);
    ctx.lineTo(bx + 2, by + bh);
    ctx.lineTo(bx, by + bh - 2);
    ctx.lineTo(bx, by + 2);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = C.bubbleBg;
    if (tailDir === 'down') {
      ctx.beginPath();
      ctx.moveTo(tailX - 4, by + bh);
      ctx.lineTo(tailX, by + bh + 6);
      ctx.lineTo(tailX + 4, by + bh);
      ctx.closePath();
      ctx.fill();
      ctx.strokeStyle = C.bubbleBdr;
      ctx.stroke();
      fill(tailX - 3, by + bh - 1, 7, 2, C.bubbleBg);
    } else {
      ctx.beginPath();
      ctx.moveTo(tailX - 4, by);
      ctx.lineTo(tailX, by - 6);
      ctx.lineTo(tailX + 4, by);
      ctx.closePath();
      ctx.fill();
      ctx.strokeStyle = C.bubbleBdr;
      ctx.stroke();
      fill(tailX - 3, by, 7, 2, C.bubbleBg);
    }
  }

  // ── Character Drawing ──

  function drawStudentSide(x, y, ps) {
    // Seated profile facing right
    // Hair
    fill(x - 2*ps, y - 8*ps, 4*ps, 2*ps, C.hair);
    fill(x - 3*ps, y - 6*ps, 5*ps, 2*ps, C.hair);
    // Head (face visible on right)
    fill(x - 2*ps, y - 6*ps, 3*ps, 4*ps, C.hair);
    fill(x + ps, y - 6*ps, 2*ps, 4*ps, C.skin);
    fill(x - ps, y - 4*ps, 2*ps, 2*ps, C.skin);
    // Eye
    fill(x + ps, y - 5*ps, ps, ps, C.eye);
    // White coat body
    fill(x - 3*ps, y - 2*ps, 5*ps, 5*ps, C.whiteCoat);
    fill(x - 2*ps, y - ps, 4*ps, 4*ps, C.coatShade);
    fill(x - 3*ps, y - 2*ps, 5*ps, 5*ps, C.whiteCoat);
    // Arm reaching to keyboard
    fill(x + 2*ps, y - ps, 4*ps, 2*ps, C.whiteCoat);
    fill(x + 6*ps, y - ps, ps, 2*ps, C.skin);
    // Legs (seated)
    fill(x - 2*ps, y + 3*ps, 5*ps, 2*ps, C.pants);
    fill(x + 3*ps, y + 3*ps, 2*ps, 2*ps, C.pants);
    // Feet
    fill(x + 4*ps, y + 5*ps, 2*ps, ps, C.shoes);
  }

  function drawStudentFront(x, y, ps) {
    drawStudentFrontColored(x, y, ps, C.whiteCoat, C.coatShade);
  }

  function drawStudentFrontColored(x, y, ps, coat, coatLine) {
    fill(x - 3*ps, y - 7*ps, 6*ps, 2*ps, C.hair);
    fill(x - 3*ps, y - 6*ps, 7*ps, 2*ps, C.hair);
    fill(x - 2*ps, y - 4*ps, 5*ps, 4*ps, C.skin);
    fill(x - ps, y - 3*ps, ps, ps, C.eye);
    fill(x + 2*ps, y - 3*ps, ps, ps, C.eye);
    fill(x - 3*ps, y, 7*ps, 5*ps, coat);
    fill(x - 4*ps, y + ps, ps, 3*ps, C.skin);
    fill(x + 4*ps, y + ps, ps, 3*ps, C.skin);
    fill(x, y + ps, ps, 3*ps, coatLine);
    fill(x - 2*ps, y + 5*ps, 2*ps, 3*ps, C.pants);
    fill(x + ps, y + 5*ps, 2*ps, 3*ps, C.pants);
    fill(x - 2*ps, y + 8*ps, 2*ps, ps, C.shoes);
    fill(x + ps, y + 8*ps, 2*ps, ps, C.shoes);
  }

  function drawPatientCrossfade(x, y, ps, t, morphStart, morphDur, fromRobot) {
    var m = Math.min(Math.max((t - morphStart) / morphDur, 0), 1);
    if (fromRobot) {
      ctx.globalAlpha = 1 - m;
      drawMirrored(drawRobot, x, y, ps);
      ctx.globalAlpha = m;
      drawMirrored(drawRealSP, x, y, ps);
      ctx.globalAlpha = 1;
      if (m > 0.5) drawNameTag(x, y + 44, '真人 SP', '#fff0e8', C.labelOrg);
      else if (m < 0.5) drawNameTag(x, y + 44, 'EasyMED', '#dceee4', C.labelGrn);
    } else {
      ctx.globalAlpha = 1 - m;
      drawMirrored(drawRealSP, x, y, ps);
      ctx.globalAlpha = m;
      drawMirrored(drawRobot, x, y, ps);
      ctx.globalAlpha = 1;
      if (m > 0.5) drawNameTag(x, y + 44, 'EasyMED', '#dceee4', C.labelGrn);
      else if (m < 0.5) drawNameTag(x, y + 44, '真人 SP', '#fff0e8', C.labelOrg);
    }
  }

  function drawRobot(x, y, ps) {
    // Antenna
    fill(x, y - 10*ps, ps, 3*ps, C.robotDark);
    fill(x - ps, y - 11*ps, 3*ps, ps, C.robotAccent);

    // Head
    fill(x - 3*ps, y - 8*ps, 7*ps, 5*ps, C.robotBody);
    fill(x - 3*ps, y - 8*ps, 7*ps, ps, C.robotDark);
    fill(x - 2*ps, y - 7*ps, 5*ps, 3*ps, C.robotLight);

    // LED eyes
    fill(x - 2*ps, y - 6*ps, 2*ps, 2*ps, C.robotEye);
    fill(x + ps, y - 6*ps, 2*ps, 2*ps, C.robotEye);
    fill(x - ps, y - 5*ps, ps, ps, '#ffffff');
    fill(x + 2*ps, y - 5*ps, ps, ps, '#ffffff');

    // Speaker grille
    fill(x - 2*ps, y - 3*ps, 5*ps, ps, C.robotDark);
    fill(x - ps, y - 3*ps, ps, ps, C.robotAccent);
    fill(x, y - 3*ps, ps, ps, C.robotAccent);
    fill(x + ps, y - 3*ps, ps, ps, C.robotAccent);

    // Neck
    fill(x - ps, y - 2*ps, 3*ps, ps, C.robotDark);

    // Body
    fill(x - 4*ps, y - ps, 9*ps, 7*ps, C.robotBody);
    fill(x - 3*ps, y, 7*ps, 5*ps, C.robotLight);
    fill(x - 4*ps, y - ps, 9*ps, ps, C.robotDark);

    // Chest screen
    fill(x - 2*ps, y + ps, 5*ps, 3*ps, '#dceee4');
    fill(x - ps, y + 2*ps, 3*ps, ps, C.robotAccent);

    // Arms
    fill(x - 6*ps, y, 2*ps, 5*ps, C.robotDark);
    fill(x + 5*ps, y, 2*ps, 5*ps, C.robotDark);
    fill(x - 6*ps, y + 5*ps, 2*ps, ps, C.robotBody);
    fill(x + 5*ps, y + 5*ps, 2*ps, ps, C.robotBody);

    // Legs
    fill(x - 3*ps, y + 6*ps, 3*ps, 3*ps, C.robotDark);
    fill(x + ps, y + 6*ps, 3*ps, 3*ps, C.robotDark);

    // Feet
    fill(x - 4*ps, y + 9*ps, 4*ps, ps, C.robotDark);
    fill(x + ps, y + 9*ps, 4*ps, ps, C.robotDark);
  }

  function drawRealSP(x, y, ps) {
    // Dark hair
    fill(x - 3*ps, y - 7*ps, 6*ps, 2*ps, C.darkHair);
    fill(x - 3*ps, y - 6*ps, 7*ps, ps, C.darkHair);
    // Head
    fill(x - 2*ps, y - 5*ps, 5*ps, 4*ps, C.skin);
    // Eyes
    fill(x - ps, y - 4*ps, ps, ps, C.eye);
    fill(x + 2*ps, y - 4*ps, ps, ps, C.eye);
    // Mouth
    fill(x, y - 2*ps, ps, ps, C.skinShade);
    // Shirt
    fill(x - 3*ps, y - ps, 7*ps, 6*ps, C.shirt);
    fill(x, y, ps, 4*ps, C.shirtShade);
    // Arms
    fill(x - 4*ps, y, ps, 3*ps, C.skin);
    fill(x + 4*ps, y, ps, 3*ps, C.skin);
    // Jeans
    fill(x - 2*ps, y + 5*ps, 2*ps, 3*ps, C.jeans);
    fill(x + ps, y + 5*ps, 2*ps, 3*ps, C.jeans);
    // Shoes
    fill(x - 2*ps, y + 8*ps, 2*ps, ps, C.shoes);
    fill(x + ps, y + 8*ps, 2*ps, ps, C.shoes);
  }

  function drawMirrored(fn, x, y, ps) {
    ctx.save();
    ctx.translate(x, 0);
    ctx.scale(-1, 1);
    ctx.translate(-x, 0);
    fn(x, y, ps);
    ctx.restore();
  }

  function drawNameTag(cx, y, label, bg, fg) {
    var tw = label.length * 7 + 10;
    var tx = cx - tw / 2;
    fill(tx, y, tw, 14, bg);
    ctx.strokeStyle = fg;
    ctx.lineWidth = 1;
    ctx.strokeRect(Math.floor(tx) + 0.5, Math.floor(y) + 0.5, tw - 1, 13);
    txt(label, cx, y + 2, fg, 8, 'center');
  }

  function drawSplitPanels() {
    fill(0, 0, W, H, C.sceneBg);
    fill(0, 0, 236, H, C.panelLeft);
    fill(244, 0, 236, H, C.panelRight);
    fill(236, 0, 8, H, C.divider);
    fill(238, 0, 4, H, C.dividerHi);
  }

  function fadeAlpha(t, start, dur) {
    return Math.min(Math.max((t - start) / dur, 0), 1);
  }

  // Exam station (desk + OSCE Test)
  function drawOsceStation(cx, baseY, t, examLabel) {
    var deskW = 72, deskH = 5;
    var dx = cx - deskW / 2;
    fill(dx, baseY, deskW, deskH, C.deskTop);
    fill(dx, baseY + deskH, deskW, 2, C.desk);
    fill(dx + 6, baseY + deskH + 2, 4, 14, C.deskLeg);
    fill(dx + deskW - 10, baseY + deskH + 2, 4, 14, C.deskLeg);

    fill(cx - 28, baseY - 38, 56, 32, '#f8f8f8');
    ctx.strokeStyle = '#888888';
    ctx.lineWidth = 1;
    ctx.strokeRect(cx - 28 + 0.5, baseY - 38 + 0.5, 55, 31);
    txt(examLabel || 'Pre-test', cx, baseY - 34, '#c0392b', 8, 'center');
    txt('OSCE Test', cx, baseY - 22, '#2980b9', 8, 'center');

    if (t > 0.5 && Math.floor(t * 3) % 2 === 0) {
      fill(cx - 4, baseY - 14, 8, 2, '#27ae60');
    }
  }

  function drawOsceExamSide(cx, t, examLabel) {
    if (t > 0.3) {
      ctx.globalAlpha = fadeAlpha(t, 0.3, 0.4);
      drawOsceStation(cx, 100, t, examLabel);
      ctx.globalAlpha = 1;
    }
    if (t > 0.6) {
      ctx.globalAlpha = fadeAlpha(t, 0.6, 0.35);
      drawStudentSide(cx + 26, 128, 2);
      ctx.globalAlpha = 1;
    }
  }

  // Mini chart — only Pre-test point (first x)
  var CHART_STU_COLORS = [
    '#4ecdc4', '#a8d8ea', '#c3b1e1', '#b5e8b0', '#d5d5d5',
    '#e8f5a0', '#ffe66d', '#ffb3b3', '#b3d9ff', '#e0c3fc',
    '#ffd4a3', '#f5c6d6', '#e8e8e8'
  ];

  function scoreToY(score, chartTop, chartH) {
    return chartTop + chartH - ((score - 40) / 60) * chartH;
  }

  function drawMiniChart(cx, cy, cw, ch, title, preScores, midScores, postScores, avgPre, avgMid, avgPost, pointCount, reveal, lineProgress) {
    var chartL = cx - cw / 2;
    var chartTop = cy;
    var plotL = chartL + 28;
    var plotW = cw - 38;
    var plotH = ch - 28;
    var plotY = chartTop + 14;
    var pop = Math.min(Math.max(reveal, 0), 1);
    var prog = Math.min(Math.max(lineProgress || 0, 0), 1);

    fill(chartL, chartTop, cw, ch, '#ffffff');
    ctx.strokeStyle = '#cccccc';
    ctx.lineWidth = 1;
    ctx.strokeRect(chartL + 0.5, chartTop + 0.5, cw - 1, ch - 1);

    txt(title, chartL + 6, chartTop + 4, '#333333', 7);

    for (var g = 40; g <= 100; g += 20) {
      var gy = scoreToY(g, plotY, plotH);
      ctx.strokeStyle = '#eeeeee';
      ctx.beginPath();
      ctx.moveTo(plotL, gy);
      ctx.lineTo(plotL + plotW, gy);
      ctx.stroke();
      txt(String(g), chartL + 4, gy - 4, '#999999', 6);
    }

    var x0 = plotL + plotW * 0.2;
    var x1 = plotL + plotW * 0.5;
    var x2 = plotL + plotW * 0.8;
    txt('Pre-test', x0 - 18, plotY + plotH + 4, pointCount >= 1 ? '#666666' : '#cccccc', 6);
    txt('Mid-test', x1 - 16, plotY + plotH + 4, pointCount >= 2 ? '#666666' : '#cccccc', 6);
    txt('Post-test', x2 - 20, plotY + plotH + 4, pointCount >= 3 ? '#666666' : '#cccccc', 6);

    function drawSeg(xa, ya, xb, yb, color, alpha, p) {
      var px = xa + (xb - xa) * p;
      var py = ya + (yb - ya) * p;
      ctx.strokeStyle = color;
      ctx.lineWidth = 1;
      ctx.globalAlpha = alpha * pop;
      ctx.beginPath();
      ctx.moveTo(xa, ya);
      ctx.lineTo(px, py);
      ctx.stroke();
      ctx.globalAlpha = 1;
    }

    function drawDot(x, y, col) {
      var r = 2;
      ctx.globalAlpha = 0.45 * pop;
      fill(x - r, y - r, r * 2, r * 2, col);
      ctx.globalAlpha = 1;
    }

    function drawAvgDot(x, y) {
      ctx.globalAlpha = pop;
      fill(x - 3, y - 3, 6, 6, '#222222');
      ctx.globalAlpha = 1;
    }

    preScores.forEach(function(sc, i) {
      var y0 = scoreToY(sc, plotY, plotH);
      var col = CHART_STU_COLORS[i % CHART_STU_COLORS.length];
      drawDot(x0, y0, col);

      if (pointCount >= 2 && midScores) {
        var y1 = scoreToY(midScores[i], plotY, plotH);
        var preMidProg = pointCount >= 3 ? 1 : prog;
        drawSeg(x0, y0, x1, y1, col, 0.45, preMidProg);
        if (preMidProg >= 0.98) drawDot(x1, y1, col);

        if (pointCount >= 3 && postScores) {
          var y2 = scoreToY(postScores[i], plotY, plotH);
          drawSeg(x1, y1, x2, y2, col, 0.45, prog);
          if (prog >= 0.98) drawDot(x2, y2, col);
        }
      }
    });

    var ay0 = scoreToY(avgPre, plotY, plotH);
    drawAvgDot(x0, ay0);

    if (pointCount >= 2 && avgMid != null) {
      var ay1 = scoreToY(avgMid, plotY, plotH);
      var preMidAvg = pointCount >= 3 ? 1 : prog;
      ctx.setLineDash([3, 2]);
      drawSeg(x0, ay0, x1, ay1, '#222222', 1, preMidAvg);
      ctx.setLineDash([]);
      if (preMidAvg >= 0.98) drawAvgDot(x1, ay1);

      if (pointCount >= 3 && avgPost != null) {
        var ay2 = scoreToY(avgPost, plotY, plotH);
        ctx.setLineDash([3, 2]);
        drawSeg(x1, ay1, x2, ay2, '#222222', 1, prog);
        ctx.setLineDash([]);
        if (prog >= 0.98) drawAvgDot(x2, ay2);
      }
    }
  }

  // ── Scene 1: Student at Computer ──

  function drawScene1(t) {
    // Wall
    fill(0, 0, W, 200, C.wall);
    for (let i = 1; i < 5; i++) fill(i * 100, 0, 1, 200, C.wallLine);

    // Floor
    fill(0, 200, W, 70, C.floor);
    for (let i = 0; i < 9; i++) fill(0, 203 + i * 8, W, 1, C.floorLine);

    // Bookshelf (left)
    fill(25, 45, 65, 100, C.shelf);
    fill(25, 45, 65, 3, '#7a6a5a');
    fill(25, 72, 65, 2, C.shelf);
    fill(25, 99, 65, 2, C.shelf);
    fill(25, 126, 65, 2, C.shelf);
    fill(25, 142, 65, 3, '#7a6a5a');
    // Books
    var bx = 29;
    [[8,22,C.bookR],[7,20,C.bookB],[9,22,C.bookG],[6,21,C.bookY],[8,22,C.bookP]].forEach(function(b) {
      fill(bx, 48, b[0], b[1], b[2]); bx += b[0] + 1;
    });
    bx = 29;
    [[10,24,C.bookB],[8,22,C.bookR],[7,24,C.bookY],[9,23,C.bookG]].forEach(function(b) {
      fill(bx, 75, b[0], b[1], b[2]); bx += b[0] + 1;
    });
    bx = 29;
    [[8,24,C.bookP],[10,22,C.bookR],[7,24,C.bookB],[8,23,C.bookG]].forEach(function(b) {
      fill(bx, 102, b[0], b[1], b[2]); bx += b[0] + 1;
    });

    // Window (right)
    fill(385, 35, 70, 85, C.winFrame);
    fill(388, 38, 30, 37, C.winGlass);
    fill(422, 38, 30, 37, C.winGlass);
    fill(388, 79, 30, 37, C.winGlass);
    fill(422, 79, 30, 37, C.winGlass);
    fill(390, 40, 12, 15, C.winLight);
    fill(424, 40, 12, 15, C.winLight);

    // Poster on wall
    fill(140, 50, 30, 40, '#ddd5c0');
    fill(142, 52, 26, 36, '#ccc5b0');
    fill(145, 55, 6, 3, '#c0392b');
    fill(145, 60, 20, 2, '#999');
    fill(145, 64, 18, 2, '#999');
    fill(145, 68, 15, 2, '#999');

    // Desk
    fill(160, 178, 190, 5, C.deskTop);
    fill(160, 183, 190, 2, C.desk);
    fill(163, 185, 4, 28, C.deskLeg);
    fill(343, 185, 4, 28, C.deskLeg);

    // Chair
    fill(220, 183, 45, 4, C.chair);
    fill(220, 195, 45, 4, C.chairSeat);
    fill(232, 199, 4, 14, C.deskLeg);
    fill(252, 199, 4, 14, C.deskLeg);

    // Monitor
    var monX = 225, monY = 118, monW = 80, monH = 55;
    fill(monX, monY, monW, monH, C.monFrame);
    fill(monX + 3, monY + 3, monW - 6, monH - 6, C.monScreen);
    fill(monX + 32, monY + monH, 16, 4, C.monFrame);
    fill(monX + 24, monY + monH + 4, 32, 3, '#b0b0b0');

    // Keyboard
    fill(270, 176, 32, 3, '#c0c0c0');
    for (var ki = 0; ki < 6; ki++) fill(272 + ki * 5, 177, 3, 1, '#d8d8d8');

    // Mouse
    fill(310, 176, 7, 4, '#c0c0c0');
    fill(312, 176, 3, 2, '#d8d8d8');

    // Monitor screen content
    if (t > 0.8) {
      var st = t - 0.8;
      // Screen glow
      var ga = 0.03 + 0.02 * Math.sin(t * 3);
      ctx.fillStyle = 'rgba(26,138,58,' + ga + ')';
      ctx.fillRect(monX + 3, monY + 3, monW - 6, monH - 6);

      var sx = monX + 10, sy = monY + 15;
      typewrite('EasyMED', sx, sy, C.monText, 8, st, 5);
      if (st > 1.5) typewrite('Virtual', sx + 4, sy + 13, C.monText, 8, st - 1.5, 5);
      if (st > 2.8) typewrite('Patient', sx + 4, sy + 26, C.monText, 8, st - 2.8, 5);

      // Blinking cursor
      if (Math.floor(t * 2.5) % 2 === 0) {
        var cy = sy, cx = sx;
        if (st > 2.8) {
          cy = sy + 26;
          cx = sx + 4 + Math.min(Math.floor((st - 2.8) * 5), 7) * 6;
        } else if (st > 1.5) {
          cy = sy + 13;
          cx = sx + 4 + Math.min(Math.floor((st - 1.5) * 5), 7) * 6;
        } else {
          cx = sx + Math.min(Math.floor(st * 5), 7) * 6;
        }
        fill(cx, cy, 5, 8, C.monText);
      }

      // Scan lines
      for (var sli = monY + 3; sli < monY + monH - 3; sli += 2) {
        ctx.fillStyle = 'rgba(26,138,58,0.04)';
        ctx.fillRect(monX + 3, sli, monW - 6, 1);
      }
    }

    // Student (seated, side view)
    if (t > 0.3) {
      var sa = Math.min((t - 0.3) * 4, 1);
      ctx.globalAlpha = sa;
      drawStudentSide(238, 192, 3);
      ctx.globalAlpha = 1;
    }

    // Ambient: subtle monitor light on desk
    if (t > 0.8) {
      ctx.fillStyle = 'rgba(26,138,58,0.03)';
      ctx.fillRect(220, 176, 90, 6);
    }
  }

  // Chart data — from reference performance plots
  var GROUP_A_PRE = [72, 75, 70, 74, 68, 78, 50];
  var GROUP_A_MID = [85, 88, 82, 90, 84, 87, 72];
  var GROUP_A_AVG_PRE = 71;
  var GROUP_A_AVG_MID = 86;
  var GROUP_B_PRE = [84, 82, 78, 74, 68, 52, 53];
  var GROUP_B_MID = [86, 94, 82, 83, 82, 73, 73];
  var GROUP_B_AVG_PRE = 70;
  var GROUP_B_AVG_MID = 82;
  var GROUP_A_POST = [93, 85, 86, 94, 84, 88, 85];
  var GROUP_A_AVG_POST = 87;
  var GROUP_B_POST = [89, 95, 84, 84, 85, 80, 80];
  var GROUP_B_AVG_POST = 85;

  // ── Scene 2: Week 0 — Pre-test ──

  function drawScene2(t) {
    var LEFT_CX = 118;
    var RIGHT_CX = 362;

    drawSplitPanels();

    if (t > 0.2) {
      ctx.globalAlpha = fadeAlpha(t, 0.2, 0.4);
      txt('Week 0：Pre-test', W / 2, 6, '#333333', 10, 'center');
      ctx.globalAlpha = 1;
    }

    if (t > 0.3) {
      ctx.globalAlpha = fadeAlpha(t, 0.3, 0.5);
      txt('Group A', LEFT_CX, 22, C.labelGrn, 9, 'center');
      txt('Group B', RIGHT_CX, 22, C.labelOrg, 9, 'center');
      ctx.globalAlpha = 1;
    }

    drawOsceExamSide(LEFT_CX, t, 'Pre-test');
    drawOsceExamSide(RIGHT_CX, t, 'Pre-test');

    if (t > 2.2) {
      var ca = fadeAlpha(t, 2.2, 0.5);
      drawMiniChart(LEFT_CX, 162, 200, 92, 'Group A Performance',
        GROUP_A_PRE, null, null, GROUP_A_AVG_PRE, null, null, 1, ca, 0);
      drawMiniChart(RIGHT_CX, 162, 200, 92, 'Group B Performance',
        GROUP_B_PRE, null, null, GROUP_B_AVG_PRE, null, null, 1, ca, 0);
    }
  }

  // ── Scene 4: Week 2 — Mid-test ──

  function drawScene4(t) {
    var LEFT_CX = 118;
    var RIGHT_CX = 362;

    drawSplitPanels();

    if (t > 0.2) {
      ctx.globalAlpha = fadeAlpha(t, 0.2, 0.4);
      txt('Week 2：Mid-test', W / 2, 6, '#333333', 10, 'center');
      ctx.globalAlpha = 1;
    }

    if (t > 0.3) {
      ctx.globalAlpha = fadeAlpha(t, 0.3, 0.5);
      txt('Group A', LEFT_CX, 22, C.labelGrn, 9, 'center');
      txt('Group B', RIGHT_CX, 22, C.labelOrg, 9, 'center');
      ctx.globalAlpha = 1;
    }

    drawOsceExamSide(LEFT_CX, t, 'Mid-test');
    drawOsceExamSide(RIGHT_CX, t, 'Mid-test');

    // Charts: Pre-test → Mid-test (line rises to second point)
    if (t > 0.8) {
      var ca = fadeAlpha(t, 0.8, 0.4);
      var lineProg = fadeAlpha(t, 1.2, 1.4);
      drawMiniChart(LEFT_CX, 162, 200, 92, 'Group A Performance',
        GROUP_A_PRE, GROUP_A_MID, null, GROUP_A_AVG_PRE, GROUP_A_AVG_MID, null, 2, ca, lineProg);
      drawMiniChart(RIGHT_CX, 162, 200, 92, 'Group B Performance',
        GROUP_B_PRE, GROUP_B_MID, null, GROUP_B_AVG_PRE, GROUP_B_AVG_MID, null, 2, ca, lineProg);
    }
  }

  // ── Scene 6: Week 4 — Final test ──

  function drawScene6(t) {
    var LEFT_CX = 118;
    var RIGHT_CX = 362;

    drawSplitPanels();

    if (t > 0.2) {
      ctx.globalAlpha = fadeAlpha(t, 0.2, 0.4);
      txt('Week 4：Final test', W / 2, 6, '#333333', 10, 'center');
      ctx.globalAlpha = 1;
    }

    if (t > 0.3) {
      ctx.globalAlpha = fadeAlpha(t, 0.3, 0.5);
      txt('Group A', LEFT_CX, 22, C.labelGrn, 9, 'center');
      txt('Group B', RIGHT_CX, 22, C.labelOrg, 9, 'center');
      ctx.globalAlpha = 1;
    }

    drawOsceExamSide(LEFT_CX, t, 'Final test');
    drawOsceExamSide(RIGHT_CX, t, 'Final test');

    // Charts: Mid-test → Post-test (line rises to third point)
    if (t > 0.8) {
      var ca = fadeAlpha(t, 0.8, 0.4);
      var lineProg = fadeAlpha(t, 1.2, 1.4);
      drawMiniChart(LEFT_CX, 162, 200, 92, 'Group A Performance',
        GROUP_A_PRE, GROUP_A_MID, GROUP_A_POST,
        GROUP_A_AVG_PRE, GROUP_A_AVG_MID, GROUP_A_AVG_POST, 3, ca, lineProg);
      drawMiniChart(RIGHT_CX, 162, 200, 92, 'Group B Performance',
        GROUP_B_PRE, GROUP_B_MID, GROUP_B_POST,
        GROUP_B_AVG_PRE, GROUP_B_AVG_MID, GROUP_B_AVG_POST, 3, ca, lineProg);
    }
  }

  // ── Training scene (Week 1 / Week 3 swap) ──

  function drawTrainingPanelAmbience(x, y, w, h, kind, t) {
    if (kind === 'digital') {
      var pulse = 0.3 + 0.15 * Math.sin(t * 4);
      ctx.fillStyle = 'rgba(26,154,92,' + (pulse * 0.05) + ')';
      ctx.fillRect(x, y, w, h);
      for (var sl = y; sl < y + h; sl += 3) {
        ctx.fillStyle = 'rgba(26,154,92,' + (0.02 + 0.012 * Math.sin(sl * 0.15 + t * 5)) + ')';
        ctx.fillRect(x, sl, w, 1);
      }
    } else {
      ctx.fillStyle = 'rgba(208,112,32,0.04)';
      ctx.fillRect(x, y, w, h);
    }
  }

  function drawTrainingPatient(patientX, t, type, panelAlpha) {
    ctx.globalAlpha = panelAlpha;
    if (type === 'robot') {
      drawMirrored(drawRobot, patientX, 108, 3);
      if (t > 1.2) drawNameTag(patientX, 152, 'EasyMED', '#dceee4', C.labelGrn);
      var glitch = Math.sin(t * 17.3) * Math.sin(t * 7.1);
      if (glitch > 0.85) {
        var gy = 96 + ((t * 137.5) % 38);
        ctx.fillStyle = 'rgba(26,154,92,0.2)';
        ctx.fillRect(patientX - 30, gy, 60, 2);
      }
    } else {
      drawMirrored(drawRealSP, patientX, 108, 3);
      if (t > 1.2) drawNameTag(patientX, 152, '真人 SP', '#fff0e8', C.labelOrg);
    }
    ctx.globalAlpha = 1;
  }

  function drawTrainingDialogue(side, t, patientType, layout) {
    var L = layout || {};
    var studentX = side === 'left' ? 62 : 306;
    var patientX = side === 'left' ? 178 : 418;
    var bubbleX = side === 'left' ? 28 : 272;
    var bubbleAnsX = side === 'left' ? 108 : 348;
    var textX = side === 'left' ? 34 : 278;
    var textAnsX = side === 'left' ? 114 : 354;
    var qStart = side === 'left' ? 2.0 : 2.5;
    var aStart = side === 'left' ? 3.5 : 4.0;
    var bubbleQY = L.bubbleStudentY != null ? L.bubbleStudentY : 138;
    var textQY = L.textStudentY != null ? L.textStudentY : 142;
    var bubbleAY = L.bubbleAnsY != null ? L.bubbleAnsY : 52;
    var textAY = L.textAnsY != null ? L.textAnsY : 56;
    var textAY2 = L.textAnsY2 != null ? L.textAnsY2 : 69;

    if (t > qStart) {
      var qt = t - qStart;
      drawBubble(bubbleX, bubbleQY, 100, 20, studentX, 'down');
      typewrite('您哪里不舒服？', textX, textQY, C.bubbleTxt, 9, qt, 6);
    }

    if (t > aStart) {
      var at = t - aStart;
      drawBubble(bubbleAnsX, bubbleAY, 118, 33, patientX, 'down');
      if (patientType === 'robot') {
        typewrite('我头疼了三天，', textAnsX, textAY, C.bubbleTxt, 9, at, 5);
        if (at > 1.4) typewrite('伴有恶心呕吐...', textAnsX, textAY2, C.bubbleTxt, 9, at - 1.4, 5);
      } else {
        typewrite('嗯...头疼，', textAnsX, textAY, C.bubbleTxt, 9, at, 4);
        if (at > 1.2) typewrite('大概三天了吧', textAnsX, textAY2, C.bubbleTxt, 9, at - 1.2, 4);
      }
    }
  }

  function scene7PatientType(side, t, morphStart, morphDur) {
    var m = Math.min(Math.max((t - morphStart) / morphDur, 0), 1);
    if (side === 'left') return m < 0.5 ? 'robot' : 'sp';
    return m < 0.5 ? 'sp' : 'robot';
  }

  function drawTrainingScene(t, opts) {
    var LEFT_CX = 118;
    var RIGHT_CX = 362;
    var STUDENT_PS = 2;
    var LEFT_PX = 178;
    var RIGHT_PX = 418;

    fill(0, 0, W, H, C.sceneBg);
    fill(0, 0, 236, H, C.panelLeft);
    fill(244, 0, 236, H, C.panelRight);
    fill(236, 0, 8, H, C.divider);
    fill(238, 0, 4, H, C.dividerHi);

    if (t > 0.2) {
      ctx.globalAlpha = Math.min((t - 0.2) * 4, 1);
      txt(opts.weekTitle, W / 2, 6, '#555555', 10, 'center');
      ctx.globalAlpha = 1;
    }

    if (t > 0.3) {
      drawTrainingPanelAmbience(5, 38, 226, 175, opts.leftAmbience, t);
      drawTrainingPanelAmbience(249, 38, 226, 175, opts.rightAmbience, t);
      var ta = Math.min((t - 0.3) * 4, 1);
      ctx.globalAlpha = ta;
      txt('Group A', LEFT_CX, 22, C.labelGrn, 10, 'center');
      txt(opts.leftTrainLabel, LEFT_CX, 34, opts.leftLabelColor, 8, 'center');
      txt('Group B', RIGHT_CX, 22, C.labelOrg, 10, 'center');
      txt(opts.rightTrainLabel, RIGHT_CX, 34, opts.rightLabelColor, 8, 'center');
      ctx.globalAlpha = 1;
    }

    fill(12, 218, 212, 2, C.floorLine);
    fill(256, 218, 212, 2, C.floorLine);

    if (t > 0.5) {
      var pa = Math.min((t - 0.5) * 4, 1);
      ctx.globalAlpha = pa;
      drawMirrored(drawStudentFront, 62, 168, STUDENT_PS);
      drawMirrored(drawStudentFront, 306, 168, STUDENT_PS);
      ctx.globalAlpha = 1;

      drawTrainingPatient(LEFT_PX, t, opts.leftPatient, pa);
      drawTrainingPatient(RIGHT_PX, t, opts.rightPatient, pa);
    }

    if (t > 1.5) {
      ctx.globalAlpha = 0.45;
      txt('学生 · 医生', 62, 200, '#666666', 7, 'center');
      txt('患者', LEFT_PX, 200, opts.leftPatient === 'robot' ? C.labelGrn : C.labelOrg, 7, 'center');
      txt('学生 · 医生', 306, 200, '#666666', 7, 'center');
      txt('患者', RIGHT_PX, 200, opts.rightPatient === 'robot' ? C.labelGrn : C.labelOrg, 7, 'center');
      ctx.globalAlpha = 1;
    }

    drawTrainingDialogue('left', t, opts.leftPatient);
    drawTrainingDialogue('right', t, opts.rightPatient);
  }

  function drawScene3(t) {
    drawTrainingScene(t, {
      weekTitle: 'Week 1 · 第一次训练',
      leftTrainLabel: 'EasyMED 训练',
      rightTrainLabel: '真人 SP 训练',
      leftLabelColor: C.labelGrn,
      rightLabelColor: C.labelOrg,
      leftPatient: 'robot',
      rightPatient: 'sp',
      leftAmbience: 'digital',
      rightAmbience: 'warm'
    });
  }

  function drawScene5(t) {
    drawTrainingScene(t, {
      weekTitle: 'Weeks 3：交换训练',
      leftTrainLabel: '真人 SP 训练',
      rightTrainLabel: 'EasyMED 训练',
      leftLabelColor: C.labelOrg,
      rightLabelColor: C.labelGrn,
      leftPatient: 'sp',
      rightPatient: 'robot',
      leftAmbience: 'warm',
      rightAmbience: 'digital'
    });
  }

  // Bar chart — Mean Score Gain (reference figure)
  var GAIN_BARS = [
    { v: 16.58, c: C.barHumanSP, g: 0 },
    { v: 21.83, c: C.barEasyMED, g: 0 },
    { v: 6.30, c: C.barHumanSP, g: 1 },
    { v: 7.10, c: C.barEasyMED, g: 1 }
  ];
  var GAIN_BAR_X = [108, 148, 318, 358];
  var GAIN_ARROW_BAR = 1;

  function drawGainBarChart(barProg) {
    var chartX = 32;
    var chartY = 158;
    var chartW = 416;
    var chartH = 104;
    var plotBottom = chartY + chartH - 22;
    var plotTop = chartY + 22;
    var plotH = plotBottom - plotTop;
    var yMax = 25;
    var barW = 26;

    fill(chartX, chartY, chartW, chartH, '#ffffff');
    ctx.strokeStyle = '#cccccc';
    ctx.lineWidth = 1;
    ctx.strokeRect(chartX + 0.5, chartY + 0.5, chartW - 1, chartH - 1);

    txt('Mean Score Gain (Mid-test - Pre-test)', chartX + chartW / 2, chartY + 4, '#333333', 7, 'center');

    for (var g = 0; g <= 25; g += 5) {
      var gy = plotBottom - (g / yMax) * plotH;
      ctx.strokeStyle = '#eeeeee';
      ctx.beginPath();
      ctx.moveTo(chartX + 36, gy);
      ctx.lineTo(chartX + chartW - 12, gy);
      ctx.stroke();
      txt(String(g), chartX + 6, gy - 4, '#999999', 6);
    }

    txt('Low Baseline', 128, plotBottom + 6, '#666666', 7, 'center');
    txt('High Baseline', 338, plotBottom + 6, '#666666', 7, 'center');

    // Legend
    fill(chartX + chartW - 118, chartY + 18, 10, 8, C.barHumanSP);
    txt('Human SP', chartX + chartW - 104, chartY + 18, '#555555', 6);
    fill(chartX + chartW - 118, chartY + 30, 10, 8, C.barEasyMED);
    txt('EasyMED', chartX + chartW - 104, chartY + 30, '#555555', 6);

    var prog = Math.min(Math.max(barProg, 0), 1);
    var arrowBarTop = 0;
    var arrowBarX = 0;

    GAIN_BARS.forEach(function(bar, i) {
      var bx = GAIN_BAR_X[i] - barW / 2;
      var fullH = (bar.v / yMax) * plotH;
      var bh = fullH * prog;
      var by = plotBottom - bh;

      ctx.fillStyle = bar.c;
      ctx.globalAlpha = 0.88;
      fill(bx, by, barW, bh, bar.c);
      ctx.strokeStyle = '#555555';
      ctx.globalAlpha = 1;
      ctx.strokeRect(bx + 0.5, by + 0.5, barW - 1, Math.max(bh - 1, 0));

      if (prog >= 0.98) {
        txt(bar.v.toFixed(2), GAIN_BAR_X[i], by - 10, '#333333', 6, 'center');
      }

      var errH = (3 + bar.v * 0.06) * prog;
      var errTop = plotBottom - bh;
      ctx.strokeStyle = '#444444';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(GAIN_BAR_X[i], errTop - errH);
      ctx.lineTo(GAIN_BAR_X[i], errTop + errH);
      ctx.moveTo(GAIN_BAR_X[i] - 4, errTop - errH);
      ctx.lineTo(GAIN_BAR_X[i] + 4, errTop - errH);
      ctx.stroke();

      if (i === GAIN_ARROW_BAR) {
        arrowBarTop = by;
        arrowBarX = GAIN_BAR_X[i];
      }
    });

    if (prog > 0.05 && arrowBarX > 0) {
      var ax0 = arrowBarX - 42;
      var ay0 = arrowBarTop - 6;
      var ax1 = arrowBarX - 6;
      var ay1 = arrowBarTop - 2;
      ctx.strokeStyle = '#c0392b';
      ctx.fillStyle = '#c0392b';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(ax0, ay0);
      ctx.lineTo(ax1, ay1);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(ax1, ay1);
      ctx.lineTo(ax1 - 5, ay1 - 3);
      ctx.lineTo(ax1 - 2, ay1 + 4);
      ctx.closePath();
      ctx.fill();
    }
  }

  // ── Scene 7: Week 1-4 — Novices Improve Fast ──

  function drawScene7(t) {
    var LEFT_CX = 118;
    var RIGHT_CX = 362;
    var STUDENT_PS = 2;
    var PATIENT_PS = 3;
    var PATIENT_X_L = 178;
    var PATIENT_X_R = 418;
    var MORPH_START = 2;
    var MORPH_DUR = 1.2;

    drawSplitPanels();

    if (t > 0.2) {
      ctx.globalAlpha = fadeAlpha(t, 0.2, 0.4);
      txt('Week 1-4：Novices Improve Fast', W / 2, 6, '#333333', 9, 'center');
      ctx.globalAlpha = 1;
    }

    if (t > 0.3) {
      ctx.globalAlpha = fadeAlpha(t, 0.3, 0.5);
      txt('Group A', LEFT_CX, 22, C.labelGrn, 9, 'center');
      txt('Group B', RIGHT_CX, 22, C.labelOrg, 9, 'center');
      ctx.globalAlpha = 1;
    }

    fill(12, 148, 212, 2, C.floorLine);
    fill(256, 148, 212, 2, C.floorLine);

    if (t > 0.5) {
      var pa = fadeAlpha(t, 0.5, 0.6);
      ctx.globalAlpha = pa;

      ctx.save();
      drawMirrored(function(x, y, ps) {
        drawStudentFrontColored(x, y, ps, C.coatGreen, C.coatGrnSh);
      }, 62, 100, STUDENT_PS);
      drawMirrored(function(x, y, ps) {
        drawStudentFrontColored(x, y, ps, C.coatBlue, C.coatBluSh);
      }, 306, 100, STUDENT_PS);
      ctx.restore();

      drawPatientCrossfade(PATIENT_X_L, 52, PATIENT_PS, t, MORPH_START, MORPH_DUR, true);
      drawPatientCrossfade(PATIENT_X_R, 52, PATIENT_PS, t, MORPH_START, MORPH_DUR, false);

      ctx.globalAlpha = 1;
    }

    var scene7DialogueLayout = {
      bubbleStudentY: 72,
      textStudentY: 76,
      bubbleAnsY: 16,
      textAnsY: 20,
      textAnsY2: 33
    };
    drawTrainingDialogue('left', t, scene7PatientType('left', t, MORPH_START, MORPH_DUR), scene7DialogueLayout);
    drawTrainingDialogue('right', t, scene7PatientType('right', t, MORPH_START, MORPH_DUR), scene7DialogueLayout);

    var barGrowDur = Math.max(SCENE7_DUR - SCENE7_BAR_HOLD - 0.3, 1);
    var barProg = fadeAlpha(t, 0.3, barGrowDur);
    drawGainBarChart(barProg);
  }

  function crossFade(elapsed, transStart, drawFrom, tFrom, drawTo, tTo) {
    var tt = (elapsed - transStart) / TRANS_DUR;
    if (tt < 0.5) {
      drawFrom(tFrom);
      ctx.fillStyle = 'rgba(255,255,255,' + (tt * 2) + ')';
      ctx.fillRect(0, 0, W, H);
    } else {
      drawTo(tTo);
      ctx.fillStyle = 'rgba(255,255,255,' + ((1 - tt) * 2) + ')';
      ctx.fillRect(0, 0, W, H);
    }
  }

  // ── Main Loop ──

  function frame(ts) {
    if (!startTs) startTs = ts;
    var elapsed = ((ts - startTs) / 1000) % TOTAL;

    ctx.imageSmoothingEnabled = false;
    ctx.clearRect(0, 0, W, H);

    if (elapsed < SCENE1_END) {
      var fadeIn = Math.min(elapsed * 2, 1);
      ctx.globalAlpha = fadeIn;
      drawScene1(elapsed);
      ctx.globalAlpha = 1;
    } else if (elapsed < TRANS1_END) {
      crossFade(elapsed, SCENE1_END, drawScene1, SCENE1_END, drawScene2, 0);
    } else if (elapsed < SCENE2_END) {
      drawScene2(elapsed - TRANS1_END);
    } else if (elapsed < TRANS2_END) {
      crossFade(elapsed, SCENE2_END, drawScene2, SCENE2_END - TRANS1_END, drawScene3, 0);
    } else if (elapsed < SCENE3_END) {
      drawScene3(elapsed - TRANS2_END);
    } else if (elapsed < TRANS3_END) {
      crossFade(elapsed, SCENE3_END, drawScene3, SCENE3_END - TRANS2_END, drawScene4, 0);
    } else if (elapsed < SCENE4_END) {
      drawScene4(elapsed - TRANS3_END);
    } else if (elapsed < TRANS4_END) {
      crossFade(elapsed, SCENE4_END, drawScene4, SCENE4_END - TRANS3_END, drawScene5, 0);
    } else if (elapsed < SCENE5_END) {
      drawScene5(elapsed - TRANS4_END);
    } else if (elapsed < TRANS5_END) {
      crossFade(elapsed, SCENE5_END, drawScene5, SCENE5_END - TRANS4_END, drawScene6, 0);
    } else if (elapsed < SCENE6_END) {
      drawScene6(elapsed - TRANS5_END);
    } else if (elapsed < TRANS6_END) {
      crossFade(elapsed, SCENE6_END, drawScene6, SCENE6_END - TRANS5_END, drawScene7, 0);
    } else if (elapsed < SCENE7_END) {
      drawScene7(elapsed - TRANS6_END);
    } else {
      var ft = (elapsed - SCENE7_END) / (FADE_END - SCENE7_END);
      drawScene7(SCENE7_END - TRANS6_END);
      ctx.fillStyle = 'rgba(255,255,255,' + Math.min(ft * 1.5, 1) + ')';
      ctx.fillRect(0, 0, W, H);
    }

    requestAnimationFrame(frame);
  }

  requestAnimationFrame(frame);
})();
