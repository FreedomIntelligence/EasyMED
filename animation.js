(() => {
  'use strict';

  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');
  const W = 480, H = 270;
  canvas.width = W;
  canvas.height = H;

  // ── Timing ──
  const TRANS_DUR = 0.5;
  let playbackTime = 0;
  let isPlaying = true;
  let isScrubbing = false;
  let lastFrameTs = null;
  let needsRedraw = true;

  // ── Data-driven timeline ──
  const SCENE_DURS = [5, 4.5, 7, 5, 9, 5, 8];
  const sceneEnd = [];
  const transEnd = [];
  let cursor = 0;
  for (let i = 0; i < SCENE_DURS.length; i++) {
    if (i === 0) {
      sceneEnd[i] = SCENE_DURS[i];
    } else {
      sceneEnd[i] = transEnd[i - 1] + SCENE_DURS[i];
    }
    transEnd[i] = sceneEnd[i] + TRANS_DUR;
  }
  const FADE_END = sceneEnd[6] + TRANS_DUR;
  const TOTAL = FADE_END;
  const SCENE7_DUR = SCENE_DURS[6];
  const SCENE7_BAR_HOLD = 0.5;

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

  // ── Structured chart data ──
  const GROUPS = {
    A: {
      pre:  [72, 75, 70, 74, 68, 78, 50],
      mid:  [85, 88, 82, 90, 84, 87, 72],
      post: [93, 85, 86, 94, 84, 88, 85],
      avgPre: 71, avgMid: 86, avgPost: 87,
    },
    B: {
      pre:  [84, 82, 78, 74, 68, 52, 53],
      mid:  [86, 94, 82, 83, 82, 73, 73],
      post: [89, 95, 84, 84, 85, 80, 80],
      avgPre: 70, avgMid: 82, avgPost: 85,
    },
  };

  // ── Utilities ──

  function fill(x, y, w, h, c) {
    ctx.fillStyle = c;
    ctx.fillRect(x | 0, y | 0, w, h);
  }

  const FONT = '"PingFang SC","Hiragino Sans GB","Microsoft YaHei","WenQuanYi Micro Hei",monospace';

  function txt(str, x, y, c, sz, al) {
    ctx.fillStyle = c;
    ctx.font = 'bold ' + sz + 'px ' + FONT;
    ctx.textAlign = al || 'left';
    ctx.textBaseline = 'top';
    ctx.fillText(str, x | 0, y | 0);
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

  function fadeAlpha(t, start, dur) {
    return Math.min(Math.max((t - start) / dur, 0), 1);
  }

  // ── Character Drawing (3-head-body ratio) ──
  // Anchor point (x,y) = center of neck/torso junction
  // Head ~6ps, Body ~6ps, Legs+feet ~6ps → total ~18ps

  function drawStudentSideColored(x, y, ps, coat, coatLine) {
    // Hair
    fill(x - 2*ps, y - 7*ps, 4*ps, 2*ps, C.hair);
    fill(x - 3*ps, y - 5*ps, 5*ps, 2*ps, C.hair);
    // Head
    fill(x - 2*ps, y - 5*ps, 3*ps, 4*ps, C.hair);
    fill(x + ps, y - 5*ps, 2*ps, 4*ps, C.skin);
    fill(x - ps, y - 3*ps, 2*ps, 2*ps, C.skin);
    // Eye
    fill(x + ps, y - 4*ps, ps, ps, C.eye);
    // Body (longer torso)
    fill(x - 3*ps, y - ps, 5*ps, 7*ps, coat);
    fill(x - 2*ps, y, 4*ps, 5*ps, coatLine);
    fill(x - 3*ps, y - ps, 5*ps, 7*ps, coat);
    // Arm
    fill(x + 2*ps, y, 4*ps, 2*ps, coat);
    fill(x + 6*ps, y, ps, 2*ps, C.skin);
    // Legs (longer)
    fill(x - 2*ps, y + 6*ps, 5*ps, 3*ps, C.pants);
    fill(x + 3*ps, y + 6*ps, 2*ps, 3*ps, C.pants);
    // Shoes
    fill(x - 2*ps, y + 9*ps, 3*ps, ps, C.shoes);
    fill(x + 4*ps, y + 9*ps, 2*ps, ps, C.shoes);
  }

  function drawStudentSide(x, y, ps) {
    drawStudentSideColored(x, y, ps, C.whiteCoat, C.coatShade);
  }

  function drawStudentFrontColored(x, y, ps, coat, coatLine) {
    // Hair
    fill(x - 3*ps, y - 7*ps, 6*ps, 2*ps, C.hair);
    fill(x - 3*ps, y - 6*ps, 7*ps, ps, C.hair);
    // Face
    fill(x - 2*ps, y - 5*ps, 5*ps, 4*ps, C.skin);
    // Eyes
    fill(x - ps, y - 4*ps, ps, ps, C.eye);
    fill(x + 2*ps, y - 4*ps, ps, ps, C.eye);
    // Body (longer torso)
    fill(x - 3*ps, y - ps, 7*ps, 7*ps, coat);
    fill(x - 4*ps, y, ps, 4*ps, C.skin);
    fill(x + 4*ps, y, ps, 4*ps, C.skin);
    fill(x, y, ps, 5*ps, coatLine);
    // Legs (longer)
    fill(x - 2*ps, y + 6*ps, 2*ps, 4*ps, C.pants);
    fill(x + ps, y + 6*ps, 2*ps, 4*ps, C.pants);
    // Shoes
    fill(x - 2*ps, y + 10*ps, 2*ps, ps, C.shoes);
    fill(x + ps, y + 10*ps, 2*ps, ps, C.shoes);
  }

  function drawStudentFront(x, y, ps) {
    drawStudentFrontColored(x, y, ps, C.whiteCoat, C.coatShade);
  }

  function drawPatientCrossfade(x, y, ps, t, morphStart, morphDur, fromRobot) {
    var m = Math.min(Math.max((t - morphStart) / morphDur, 0), 1);
    var tagY = y + 13*ps;
    if (fromRobot) {
      ctx.globalAlpha = 1 - m;
      drawMirrored(drawRobot, x, y, ps);
      ctx.globalAlpha = m;
      drawMirrored(drawRealSP, x, y, ps);
      ctx.globalAlpha = 1;
      if (m > 0.5) drawNameTag(x, tagY, 'Human SP', '#fff0e8', C.labelOrg);
      else if (m < 0.5) drawNameTag(x, tagY, 'EasyMED', '#dceee4', C.labelGrn);
    } else {
      ctx.globalAlpha = 1 - m;
      drawMirrored(drawRealSP, x, y, ps);
      ctx.globalAlpha = m;
      drawMirrored(drawRobot, x, y, ps);
      ctx.globalAlpha = 1;
      if (m > 0.5) drawNameTag(x, tagY, 'EasyMED', '#dceee4', C.labelGrn);
      else if (m < 0.5) drawNameTag(x, tagY, 'Human SP', '#fff0e8', C.labelOrg);
    }
  }

  function drawRobot(x, y, ps) {
    // Antenna
    fill(x, y - 9*ps, ps, 3*ps, C.robotDark);
    fill(x - ps, y - 10*ps, 3*ps, ps, C.robotAccent);
    // Head (6ps)
    fill(x - 3*ps, y - 7*ps, 7*ps, 5*ps, C.robotBody);
    fill(x - 3*ps, y - 7*ps, 7*ps, ps, C.robotDark);
    fill(x - 2*ps, y - 6*ps, 5*ps, 3*ps, C.robotLight);
    // LED eyes
    fill(x - 2*ps, y - 5*ps, 2*ps, 2*ps, C.robotEye);
    fill(x + ps, y - 5*ps, 2*ps, 2*ps, C.robotEye);
    fill(x - ps, y - 4*ps, ps, ps, '#ffffff');
    fill(x + 2*ps, y - 4*ps, ps, ps, '#ffffff');
    // Speaker grille
    fill(x - 2*ps, y - 2*ps, 5*ps, ps, C.robotDark);
    fill(x - ps, y - 2*ps, ps, ps, C.robotAccent);
    fill(x, y - 2*ps, ps, ps, C.robotAccent);
    fill(x + ps, y - 2*ps, ps, ps, C.robotAccent);
    // Neck
    fill(x - ps, y - ps, 3*ps, ps, C.robotDark);
    // Body (longer: 8ps)
    fill(x - 4*ps, y, 9*ps, 8*ps, C.robotBody);
    fill(x - 3*ps, y + ps, 7*ps, 6*ps, C.robotLight);
    fill(x - 4*ps, y, 9*ps, ps, C.robotDark);
    // Chest screen
    fill(x - 2*ps, y + 2*ps, 5*ps, 3*ps, '#dceee4');
    fill(x - ps, y + 3*ps, 3*ps, ps, C.robotAccent);
    // Arms (longer)
    fill(x - 6*ps, y + ps, 2*ps, 6*ps, C.robotDark);
    fill(x + 5*ps, y + ps, 2*ps, 6*ps, C.robotDark);
    fill(x - 6*ps, y + 7*ps, 2*ps, ps, C.robotBody);
    fill(x + 5*ps, y + 7*ps, 2*ps, ps, C.robotBody);
    // Legs (longer: 5ps)
    fill(x - 3*ps, y + 8*ps, 3*ps, 4*ps, C.robotDark);
    fill(x + ps, y + 8*ps, 3*ps, 4*ps, C.robotDark);
    // Feet
    fill(x - 4*ps, y + 12*ps, 4*ps, ps, C.robotDark);
    fill(x + ps, y + 12*ps, 4*ps, ps, C.robotDark);
  }

  function drawRealSP(x, y, ps) {
    // Hair
    fill(x - 3*ps, y - 7*ps, 6*ps, 2*ps, C.darkHair);
    fill(x - 3*ps, y - 6*ps, 7*ps, ps, C.darkHair);
    // Face
    fill(x - 2*ps, y - 5*ps, 5*ps, 4*ps, C.skin);
    // Eyes
    fill(x - ps, y - 4*ps, ps, ps, C.eye);
    fill(x + 2*ps, y - 4*ps, ps, ps, C.eye);
    // Mouth
    fill(x, y - 2*ps, ps, ps, C.skinShade);
    // Shirt (longer torso)
    fill(x - 3*ps, y - ps, 7*ps, 7*ps, C.shirt);
    fill(x, y, ps, 5*ps, C.shirtShade);
    // Arms (longer)
    fill(x - 4*ps, y, ps, 4*ps, C.skin);
    fill(x + 4*ps, y, ps, 4*ps, C.skin);
    // Jeans (longer legs)
    fill(x - 2*ps, y + 6*ps, 2*ps, 4*ps, C.jeans);
    fill(x + ps, y + 6*ps, 2*ps, 4*ps, C.jeans);
    // Shoes
    fill(x - 2*ps, y + 10*ps, 2*ps, ps, C.shoes);
    fill(x + ps, y + 10*ps, 2*ps, ps, C.shoes);
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
    ctx.strokeRect((tx | 0) + 0.5, (y | 0) + 0.5, tw - 1, 13);
    txt(label, cx, y + 2, fg, 8, 'center');
  }

  function drawSplitPanels() {
    fill(0, 0, W, H, C.sceneBg);
    fill(0, 0, 236, H, C.panelLeft);
    fill(244, 0, 236, H, C.panelRight);
    fill(236, 0, 8, H, C.divider);
    fill(238, 0, 4, H, C.dividerHi);
  }

  // ── Chart helpers (extracted from drawMiniChart for GC) ──

  var CHART_STU_COLORS = [
    '#4ecdc4', '#a8d8ea', '#c3b1e1', '#b5e8b0', '#d5d5d5',
    '#e8f5a0', '#ffe66d', '#ffb3b3', '#b3d9ff', '#e0c3fc',
    '#ffd4a3', '#f5c6d6', '#e8e8e8'
  ];

  function scoreToY(score, chartTop, chartH) {
    return chartTop + chartH - ((score - 40) / 60) * chartH;
  }

  function chartDrawSeg(xa, ya, xb, yb, color, alpha, pop, p) {
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

  function chartDrawDot(x, y, col, pop) {
    ctx.globalAlpha = 0.45 * pop;
    fill(x - 2, y - 2, 4, 4, col);
    ctx.globalAlpha = 1;
  }

  function chartDrawAvgDot(x, y, pop) {
    ctx.globalAlpha = pop;
    fill(x - 3, y - 3, 6, 6, '#222222');
    ctx.globalAlpha = 1;
  }

  // Exam station
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

  function drawOsceExamSide(cx, t, examLabel, coat, coatLine) {
    if (t > 0.3) {
      ctx.globalAlpha = fadeAlpha(t, 0.3, 0.4);
      drawOsceStation(cx, 100, t, examLabel);
      ctx.globalAlpha = 1;
    }
    if (t > 0.6) {
      ctx.globalAlpha = fadeAlpha(t, 0.6, 0.35);
      drawStudentSideColored(cx - 27, 100, 3, coat || C.whiteCoat, coatLine || C.coatShade);
      drawNameTag(cx - 27, 134, 'Student', '#eef1f6', '#555555');
      ctx.globalAlpha = 1;
    }
  }

  // ── Mini Chart ──

  function drawMiniChart(cx, cy, cw, ch, title, grp, pointCount, reveal, lineProgress) {
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

    grp.pre.forEach(function(sc, i) {
      var y0 = scoreToY(sc, plotY, plotH);
      var col = CHART_STU_COLORS[i % CHART_STU_COLORS.length];
      chartDrawDot(x0, y0, col, pop);

      if (pointCount >= 2) {
        var y1 = scoreToY(grp.mid[i], plotY, plotH);
        var preMidProg = pointCount >= 3 ? 1 : prog;
        chartDrawSeg(x0, y0, x1, y1, col, 0.45, pop, preMidProg);
        if (preMidProg >= 0.98) chartDrawDot(x1, y1, col, pop);

        if (pointCount >= 3) {
          var y2 = scoreToY(grp.post[i], plotY, plotH);
          chartDrawSeg(x1, y1, x2, y2, col, 0.45, pop, prog);
          if (prog >= 0.98) chartDrawDot(x2, y2, col, pop);
        }
      }
    });

    var ay0 = scoreToY(grp.avgPre, plotY, plotH);
    chartDrawAvgDot(x0, ay0, pop);

    if (pointCount >= 2) {
      var ay1 = scoreToY(grp.avgMid, plotY, plotH);
      var preMidAvg = pointCount >= 3 ? 1 : prog;
      ctx.setLineDash([3, 2]);
      chartDrawSeg(x0, ay0, x1, ay1, '#222222', 1, pop, preMidAvg);
      ctx.setLineDash([]);
      if (preMidAvg >= 0.98) chartDrawAvgDot(x1, ay1, pop);

      if (pointCount >= 3) {
        var ay2 = scoreToY(grp.avgPost, plotY, plotH);
        ctx.setLineDash([3, 2]);
        chartDrawSeg(x1, ay1, x2, ay2, '#222222', 1, pop, prog);
        ctx.setLineDash([]);
        if (prog >= 0.98) chartDrawAvgDot(x2, ay2, pop);
      }
    }
  }

  // ── Scene 1: Title ──

  function drawScene1(t) {
    fill(0, 0, W, H, C.sceneBg);

    if (t > 0.3) {
      var st = t - 0.3;
      typewrite('Real-World User Study', W / 2, H / 2 - 8, '#333333', 14, st, 6, 'center');
    }
  }

  // ── Scene 2: Week 0 — Pre-test ──

  function drawScene2(t) {
    var LEFT_CX = 118, RIGHT_CX = 362;
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

    drawOsceExamSide(LEFT_CX, t, 'Pre-test', C.coatGreen, C.coatGrnSh);
    drawOsceExamSide(RIGHT_CX, t, 'Pre-test', C.coatBlue, C.coatBluSh);

    if (t > 2.2) {
      var ca = fadeAlpha(t, 2.2, 0.5);
      drawMiniChart(LEFT_CX, 162, 200, 92, 'Group A Performance', GROUPS.A, 1, ca, 0);
      drawMiniChart(RIGHT_CX, 162, 200, 92, 'Group B Performance', GROUPS.B, 1, ca, 0);
    }
  }

  // ── Scene 3: Week 1 — First training ──

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
      drawMirrored(drawRobot, patientX, 115, 4);
      drawNameTag(patientX, 167, 'EasyMED', '#dceee4', C.labelGrn);
      var glitch = Math.sin(t * 17.3) * Math.sin(t * 7.1);
      if (glitch > 0.85) {
        var gy = 96 + ((t * 137.5) % 38);
        ctx.fillStyle = 'rgba(26,154,92,0.2)';
        ctx.fillRect(patientX - 30, gy, 60, 2);
      }
    } else {
      drawMirrored(drawRealSP, patientX, 115, 4);
      drawNameTag(patientX, 167, 'Human SP', '#fff0e8', C.labelOrg);
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
      drawBubble(bubbleX, bubbleQY, 140, 20, studentX, 'down');
      typewrite('What seems to bother you?', textX, textQY, C.bubbleTxt, 8, qt, 6);
    }

    if (t > aStart) {
      var at = t - aStart;
      drawBubble(bubbleAnsX, bubbleAY, 128, 33, patientX, 'down');
      if (patientType === 'robot') {
        typewrite('Headache for 3 days,', textAnsX, textAY, C.bubbleTxt, 9, at, 5);
        if (at > 1.4) typewrite('with nausea & vomiting...', textAnsX, textAY2, C.bubbleTxt, 9, at - 1.4, 5);
      } else {
        typewrite('Um...headache,', textAnsX, textAY, C.bubbleTxt, 9, at, 4);
        if (at > 1.2) typewrite('about 3 days I think', textAnsX, textAY2, C.bubbleTxt, 9, at - 1.2, 4);
      }
    }
  }

  function drawTrainingScene(t, opts) {
    var LEFT_CX = 118, RIGHT_CX = 362;
    var STUDENT_PS = 3;
    var LEFT_PX = 178, RIGHT_PX = 418;

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
      drawMirrored(function(x, y, ps) {
        drawStudentFrontColored(x, y, ps, C.coatGreen, C.coatGrnSh);
      }, 62, 175, STUDENT_PS);
      drawMirrored(function(x, y, ps) {
        drawStudentFrontColored(x, y, ps, C.coatBlue, C.coatBluSh);
      }, 306, 175, STUDENT_PS);
      drawNameTag(62, 210, 'Student', '#eef1f6', '#555555');
      drawNameTag(306, 210, 'Student', '#eef1f6', '#555555');
      ctx.globalAlpha = 1;

      drawTrainingPatient(LEFT_PX, t, opts.leftPatient, pa);
      drawTrainingPatient(RIGHT_PX, t, opts.rightPatient, pa);
    }

    drawTrainingDialogue('left', t, opts.leftPatient);
    drawTrainingDialogue('right', t, opts.rightPatient);
  }

  function drawScene3(t) {
    drawTrainingScene(t, {
      weekTitle: 'Week 1 · First Training',
      leftTrainLabel: 'EasyMED Training',
      rightTrainLabel: 'Human SP Training',
      leftLabelColor: C.labelGrn,
      rightLabelColor: C.labelOrg,
      leftPatient: 'robot',
      rightPatient: 'sp',
      leftAmbience: 'digital',
      rightAmbience: 'warm'
    });
  }

  // ── Scene 4: Week 2 — Mid-test ──

  function drawScene4(t) {
    var LEFT_CX = 118, RIGHT_CX = 362;
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

    drawOsceExamSide(LEFT_CX, t, 'Mid-test', C.coatGreen, C.coatGrnSh);
    drawOsceExamSide(RIGHT_CX, t, 'Mid-test', C.coatBlue, C.coatBluSh);

    if (t > 0.8) {
      var ca = fadeAlpha(t, 0.8, 0.4);
      var lineProg = fadeAlpha(t, 1.2, 1.4);
      drawMiniChart(LEFT_CX, 162, 200, 92, 'Group A Performance', GROUPS.A, 2, ca, lineProg);
      drawMiniChart(RIGHT_CX, 162, 200, 92, 'Group B Performance', GROUPS.B, 2, ca, lineProg);
    }
  }

  // ── Scene 5: Week 3 — Swap training ──

  function drawScene5(t) {
    var LEFT_CX = 118, RIGHT_CX = 362;
    var STUDENT_PS = 3;
    var LEFT_PX = 178, RIGHT_PX = 418;
    var SWAP_DUR = 1.8;
    var SWAP_START = 0.3;
    var SWAP_END = SWAP_START + SWAP_DUR;

    fill(0, 0, W, H, C.sceneBg);
    fill(0, 0, 236, H, C.panelLeft);
    fill(244, 0, 236, H, C.panelRight);
    fill(236, 0, 8, H, C.divider);
    fill(238, 0, 4, H, C.dividerHi);

    if (t > 0.2) {
      ctx.globalAlpha = Math.min((t - 0.2) * 4, 1);
      txt('Week 3 · Swap Training', W / 2, 6, '#555555', 10, 'center');
      ctx.globalAlpha = 1;
    }

    // Swap animation phase
    if (t < SWAP_END + 0.3) {
      var sp = Math.min(Math.max((t - SWAP_START) / SWAP_DUR, 0), 1);
      var ease = sp < 0.5 ? 2*sp*sp : 1 - 2*(1-sp)*(1-sp);

      // Robot: left panel (178) → right panel (418)
      var robotX = LEFT_PX + (RIGHT_PX - LEFT_PX) * ease;
      // SP: right panel (418) → left panel (178)
      var spX = RIGHT_PX + (LEFT_PX - RIGHT_PX) * ease;

      // Arc: characters rise then descend during swap
      var arc = Math.sin(sp * Math.PI) * 30;
      var robotY = 115 - arc;
      var spY = 115 - arc;

      ctx.globalAlpha = fadeAlpha(t, 0.2, 0.4);
      drawMirrored(drawRobot, robotX, robotY, 4);
      drawMirrored(drawRealSP, spX, spY, 4);

      // Labels follow characters
      if (sp < 0.98) {
        drawNameTag(robotX, robotY + 52, 'EasyMED', '#dceee4', C.labelGrn);
        drawNameTag(spX, spY + 44, 'Human SP', '#fff0e8', C.labelOrg);
      }
      ctx.globalAlpha = 1;

      // Swap hint arrows
      if (sp > 0.05 && sp < 0.95) {
        ctx.globalAlpha = 0.4 * Math.sin(sp * Math.PI);
        txt('⇄', W / 2, 108, '#888888', 16, 'center');
        ctx.globalAlpha = 1;
      }
    }

    // After swap: normal training scene content with time offset
    var trainT = t - SWAP_END;
    if (trainT < 0) return;

    if (trainT > 0.1) {
      drawTrainingPanelAmbience(5, 38, 226, 175, 'warm', t);
      drawTrainingPanelAmbience(249, 38, 226, 175, 'digital', t);
      var ta = Math.min((trainT - 0.1) * 4, 1);
      ctx.globalAlpha = ta;
      txt('Group A', LEFT_CX, 22, C.labelGrn, 10, 'center');
      txt('Human SP Training', LEFT_CX, 34, C.labelOrg, 8, 'center');
      txt('Group B', RIGHT_CX, 22, C.labelOrg, 10, 'center');
      txt('EasyMED Training', RIGHT_CX, 34, C.labelGrn, 8, 'center');
      ctx.globalAlpha = 1;
    }

    fill(12, 218, 212, 2, C.floorLine);
    fill(256, 218, 212, 2, C.floorLine);

    if (trainT > 0.3) {
      var pa = Math.min((trainT - 0.3) * 4, 1);
      ctx.globalAlpha = pa;
      drawMirrored(function(x, y, ps) {
        drawStudentFrontColored(x, y, ps, C.coatGreen, C.coatGrnSh);
      }, 62, 175, STUDENT_PS);
      drawMirrored(function(x, y, ps) {
        drawStudentFrontColored(x, y, ps, C.coatBlue, C.coatBluSh);
      }, 306, 175, STUDENT_PS);
      drawNameTag(62, 210, 'Student', '#eef1f6', '#555555');
      drawNameTag(306, 210, 'Student', '#eef1f6', '#555555');
      ctx.globalAlpha = 1;

      drawTrainingPatient(LEFT_PX, trainT, 'sp', pa);
      drawTrainingPatient(RIGHT_PX, trainT, 'robot', pa);
    }

    drawTrainingDialogue('left', trainT, 'sp');
    drawTrainingDialogue('right', trainT, 'robot');
  }

  // ── Scene 6: Week 4 — Final test ──

  function drawScene6(t) {
    var LEFT_CX = 118, RIGHT_CX = 362;
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

    drawOsceExamSide(LEFT_CX, t, 'Final test', C.coatGreen, C.coatGrnSh);
    drawOsceExamSide(RIGHT_CX, t, 'Final test', C.coatBlue, C.coatBluSh);

    if (t > 0.8) {
      var ca = fadeAlpha(t, 0.8, 0.4);
      var lineProg = fadeAlpha(t, 1.2, 1.4);
      drawMiniChart(LEFT_CX, 162, 200, 92, 'Group A Performance', GROUPS.A, 3, ca, lineProg);
      drawMiniChart(RIGHT_CX, 162, 200, 92, 'Group B Performance', GROUPS.B, 3, ca, lineProg);
    }
  }

  // ── Bar chart — Mean Score Gain ──

  var GAIN_BARS = [
    { v: 16.58, c: C.barHumanSP, g: 0 },
    { v: 21.83, c: C.barEasyMED, g: 0 },
    { v: 6.30, c: C.barHumanSP, g: 1 },
    { v: 7.10, c: C.barEasyMED, g: 1 }
  ];
  var GAIN_BAR_X = [108, 148, 318, 358];
  var GAIN_ARROW_BAR = 1;

  function drawGainBarChart(barProgs) {
    var chartX = 32, chartY = 158, chartW = 416, chartH = 104;
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

    fill(chartX + chartW - 118, chartY + 18, 10, 8, C.barHumanSP);
    txt('Human SP', chartX + chartW - 104, chartY + 18, '#555555', 6);
    fill(chartX + chartW - 118, chartY + 30, 10, 8, C.barEasyMED);
    txt('EasyMED', chartX + chartW - 104, chartY + 30, '#555555', 6);

    var arrowBarTop = 0, arrowBarX = 0;
    var allDone = true;

    GAIN_BARS.forEach(function(bar, i) {
      var prog = Math.min(Math.max(barProgs[i] || 0, 0), 1);
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
      } else {
        allDone = false;
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

    if (allDone && arrowBarX > 0) {
      var ax0 = arrowBarX - 42, ay0 = arrowBarTop - 6;
      var ax1 = arrowBarX - 6, ay1 = arrowBarTop - 2;
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

  function scene7PatientType(side, t, morphStart, morphDur) {
    var m = Math.min(Math.max((t - morphStart) / morphDur, 0), 1);
    if (side === 'left') return m < 0.5 ? 'robot' : 'sp';
    return m < 0.5 ? 'sp' : 'robot';
  }

  function drawScene7(t) {
    var LEFT_CX = 118, RIGHT_CX = 362;
    var STUDENT_PS = 3, PATIENT_PS = 4;
    var PATIENT_X_L = 178, PATIENT_X_R = 418;
    var MORPH_START = 2, MORPH_DUR = 1.2;

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
      }, 62, 105, STUDENT_PS);
      drawMirrored(function(x, y, ps) {
        drawStudentFrontColored(x, y, ps, C.coatBlue, C.coatBluSh);
      }, 306, 105, STUDENT_PS);
      ctx.restore();

      drawPatientCrossfade(PATIENT_X_L, 58, PATIENT_PS, t, MORPH_START, MORPH_DUR, true);
      drawPatientCrossfade(PATIENT_X_R, 58, PATIENT_PS, t, MORPH_START, MORPH_DUR, false);

      drawNameTag(62, 140, 'Student', '#eef1f6', '#555555');
      drawNameTag(306, 140, 'Student', '#eef1f6', '#555555');

      ctx.globalAlpha = 1;
    }

    var scene7DialogueLayout = {
      bubbleStudentY: 72, textStudentY: 76,
      bubbleAnsY: 16, textAnsY: 20, textAnsY2: 33
    };
    drawTrainingDialogue('left', t, scene7PatientType('left', t, MORPH_START, MORPH_DUR), scene7DialogueLayout);
    drawTrainingDialogue('right', t, scene7PatientType('right', t, MORPH_START, MORPH_DUR), scene7DialogueLayout);

    // Per-bar growth: different easing powers, all reach 1.0 at BAR_GROW_END
    var BAR_GROW_END = 7;
    var BAR_DELAYS = [0.3, 1.0, 0.6, 1.5];
    var BAR_EASINGS = [2.2, 1.4, 1.8, 1.2];
    var barProgs = GAIN_BARS.map(function(_, i) {
      var raw = Math.min(Math.max((t - BAR_DELAYS[i]) / (BAR_GROW_END - BAR_DELAYS[i]), 0), 1);
      return Math.pow(raw, 1 / BAR_EASINGS[i]);
    });
    drawGainBarChart(barProgs);
  }

  // ── Scene router ──

  const sceneFns = [drawScene1, drawScene2, drawScene3, drawScene4, drawScene5, drawScene6, drawScene7];

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

  function renderAt(elapsed) {
    ctx.imageSmoothingEnabled = false;
    ctx.clearRect(0, 0, W, H);

    // Scene 1 fade-in
    if (elapsed < sceneEnd[0]) {
      var fadeIn = Math.min(elapsed * 2, 1);
      ctx.globalAlpha = fadeIn;
      drawScene1(elapsed);
      ctx.globalAlpha = 1;
      return;
    }

    // Scenes 1-7 with transitions
    for (var i = 0; i < 6; i++) {
      // Transition i -> i+1
      if (elapsed < transEnd[i]) {
        var prevStart = i === 0 ? 0 : transEnd[i - 1];
        crossFade(elapsed, sceneEnd[i], sceneFns[i], sceneEnd[i] - prevStart, sceneFns[i + 1], 0);
        return;
      }
      // Scene i+1
      if (elapsed < sceneEnd[i + 1]) {
        sceneFns[i + 1](elapsed - transEnd[i]);
        return;
      }
    }

    // Transition 6->end (fade out after scene 7)
    if (elapsed < FADE_END) {
      var ft = (elapsed - sceneEnd[6]) / (FADE_END - sceneEnd[6]);
      drawScene7(sceneEnd[6] - transEnd[5]);
      ctx.fillStyle = 'rgba(255,255,255,' + Math.min(ft * 1.5, 1) + ')';
      ctx.fillRect(0, 0, W, H);
    }
  }

  // ── Playback Controls (cached DOM refs) ──

  var $slider = null, $cur = null, $btn = null, $total = null;

  function formatTime(sec) {
    var s = Math.max(0, Math.min(sec, TOTAL));
    var m = Math.floor(s / 60);
    var r = Math.floor(s % 60);
    return m + ':' + (r < 10 ? '0' : '') + r;
  }

  function updateProgressUI() {
    if (!$slider || !$cur) return;
    if (!isScrubbing) $slider.value = String(playbackTime);
    $cur.textContent = formatTime(playbackTime);
  }

  function initPlaybackControls() {
    $slider = document.getElementById('progress');
    $btn = document.getElementById('btn-play');
    $cur = document.getElementById('time-cur');
    $total = document.getElementById('time-total');
    if (!$slider || !$btn || !$total) return;

    $slider.max = String(TOTAL);
    $slider.value = '0';
    $total.textContent = formatTime(TOTAL);

    function setPlayIcon() {
      $btn.textContent = isPlaying ? '⏸' : '▶';
      $btn.setAttribute('aria-label', isPlaying ? 'Pause' : 'Play');
    }

    $btn.addEventListener('click', function() {
      isPlaying = !isPlaying;
      lastFrameTs = null;
      needsRedraw = true;
      setPlayIcon();
    });

    $slider.addEventListener('pointerdown', function() {
      isScrubbing = true;
      needsRedraw = true;
    });

    $slider.addEventListener('input', function() {
      playbackTime = parseFloat($slider.value) || 0;
      needsRedraw = true;
      updateProgressUI();
    });

    $slider.addEventListener('pointerup', function() {
      isScrubbing = false;
      lastFrameTs = null;
      needsRedraw = true;
    });

    $slider.addEventListener('change', function() {
      isScrubbing = false;
      playbackTime = parseFloat($slider.value) || 0;
      lastFrameTs = null;
      needsRedraw = true;
      updateProgressUI();
    });

    setPlayIcon();
    updateProgressUI();
  }

  // ── Main Loop ──

  function frame(ts) {
    if (lastFrameTs != null && isPlaying && !isScrubbing) {
      playbackTime += (ts - lastFrameTs) / 1000;
      if (playbackTime >= TOTAL) playbackTime = 0;
      needsRedraw = true;
    }
    lastFrameTs = ts;

    if (needsRedraw) {
      renderAt(playbackTime);
      updateProgressUI();
      needsRedraw = false;
    }

    requestAnimationFrame(frame);
  }

  initPlaybackControls();
  requestAnimationFrame(frame);
})();
