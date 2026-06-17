const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        AlignmentType, BorderStyle, WidthType, ShadingType, HeadingLevel } = require('docx');
const fs = require('fs');

const border = { style: BorderStyle.SINGLE, size: 1, color: 'AAAAAA' };
const borders = { top: border, bottom: border, left: border, right: border };

function hdrCell(text, width) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: '1F3864', type: ShadingType.CLEAR },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({
      alignment: AlignmentType.LEFT,
      children: [new TextRun({ text, bold: true, color: 'FFFFFF', font: 'Arial', size: 18 })]
    })]
  });
}

function dataCell(text, width, shade) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: shade, type: ShadingType.CLEAR },
    margins: { top: 60, bottom: 60, left: 120, right: 120 },
    children: [new Paragraph({
      children: [new TextRun({ text: String(text), font: 'Courier New', size: 16 })]
    })]
  });
}

function reasonCell(text, width, shade) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: shade, type: ShadingType.CLEAR },
    margins: { top: 60, bottom: 60, left: 120, right: 120 },
    children: [new Paragraph({
      children: [new TextRun({ text, font: 'Arial', size: 16 })]
    })]
  });
}

// 36 ELIMINATE — from quality_check.py run on selmark_respuestas_2026-06-12
const eliminate = [
  { id: '6a29209c-265f-e71f-e96c-5fcb7501ddd0', dur: '7.2',  reason: 'Too fast (7.2 min). All emotional attributes rated 5 (straight-lining).' },
  { id: '6a292091-195e-4f29-b6f2-f72a8e236d91', dur: '6.6',  reason: 'Too fast (6.6 min). Invalid age (688988). All 4 lifestyle blocks uniform.' },
  { id: '6a291fea-d412-bb49-2100-9599a8f53203', dur: '7.6',  reason: 'Too fast (7.6 min). All 4 lifestyle blocks rated 3 (straight-lining).' },
  { id: '6a291fe4-47dc-4bc8-285d-a3b83e766ae6', dur: '6.8',  reason: 'Too fast (6.8 min).' },
  { id: '6a291fc2-f100-2d25-0263-f6d19518e7a7', dur: '3.9',  reason: 'Too fast (3.9 min). All emotional attributes rated 1 (straight-lining).' },
  { id: '6a291faf-664a-bb8f-d3ee-fda30a5af0e5', dur: '7.8',  reason: 'Too fast (7.8 min).' },
  { id: '6a291fa9-4900-1d14-7676-c749d6430317', dur: '7.6',  reason: 'Too fast (7.6 min). All 12 functional attributes rated 4. Open text too short.' },
  { id: '6a291f91-2840-0118-4b9e-b5f884b99d8c', dur: '8.5',  reason: 'All open-text answers too short (2 chars each) across multiple questions.' },
  { id: '6a291f72-6e0e-7967-29d6-bc2b5c1c766b', dur: '7.0',  reason: 'Too fast (7.0 min).' },
  { id: '6a291f71-e882-63de-9723-e56a24d2a8fa', dur: '6.6',  reason: 'Too fast (6.6 min). Copy-paste: same answer for unrelated questions (q46=q76).' },
  { id: '6a291f6f-e6aa-2384-c079-74ca761bd0c4', dur: '4.6',  reason: 'Too fast (4.6 min).' },
  { id: '6a291f4d-8dfd-1885-c1e3-8696525e5b70', dur: '7.4',  reason: 'Too fast (7.4 min). 3/4 lifestyle blocks all rated 5 (straight-lining).' },
  { id: '6a291c33-f1b0-859a-3d4f-949fe81c92ec', dur: '12.0', reason: 'Copy-paste: identical answers across like/dislike questions (q73=q74=q78=q79).' },
  { id: '6a291b7e-5990-d74f-0832-e83cba3bc9bc', dur: '7.0',  reason: 'Too fast (7.0 min).' },
  { id: '6a291b0e-f761-b75f-1dee-0fe962611155', dur: '7.5',  reason: 'Too fast (7.5 min). All 12 functional + all 7 emotional attributes same value.' },
  { id: '6a291aa5-5f33-0e01-75c9-1c1d9f4fab71', dur: '8.0',  reason: 'Too fast (8.0 min).' },
  { id: '6a291a5b-9f12-2f7a-2f2b-e89b1245ecec', dur: '7.1',  reason: 'Too fast (7.1 min).' },
  { id: '6a291890-4a1a-34f5-4690-b7cb222327d7', dur: '7.7',  reason: 'Too fast (7.7 min).' },
  { id: '6a29182d-4110-843c-f958-d780c8f9cc99', dur: '7.7',  reason: 'Too fast (7.7 min). 3/4 lifestyle blocks all rated 4 (straight-lining).' },
  { id: '6a291804-b0f1-5892-d6cf-56bb13dd8fe9', dur: '6.0',  reason: 'Too fast (6.0 min).' },
  { id: '6a2917fc-50a2-201c-d595-452ace3b3020', dur: '13.9', reason: 'All 4 lifestyle blocks uniformly rated 3 (no differentiation across themes).' },
  { id: '6a2917e3-5446-8845-fd07-89fb3e5006b6', dur: '5.3',  reason: 'Too fast (5.3 min).' },
  { id: '6a291753-b9d5-240c-26fa-593bafe24ce3', dur: '15.7', reason: 'All 12 functional attributes rated 5. All 7 emotional attributes rated 5.' },
  { id: '6a291751-1fac-484d-7444-0f7875348cb8', dur: '6.6',  reason: 'Too fast (6.6 min). 3/4 lifestyle blocks all rated 1 (extreme straight-lining).' },
  { id: '6a2916df-3692-4363-18f5-d1d3016bb7f6', dur: '6.8',  reason: 'Too fast (6.8 min). All functional + emotional attributes rated 3.' },
  { id: '6a2916ab-2459-b056-ea42-168d3f5d40bc', dur: '7.9',  reason: 'Too fast (7.9 min). 3/4 lifestyle blocks all rated 4 (straight-lining).' },
  { id: '6a29169f-264f-86fb-c061-57c83a76b216', dur: '6.1',  reason: 'Too fast (6.1 min).' },
  { id: '6a2915da-d933-1464-2bad-e72bcc7ef18d', dur: '9.3',  reason: 'All 6 functional attributes rated 3. All 7 emotional attributes rated 3.' },
  { id: '6a291595-5288-a77d-235d-7237c361bebf', dur: '7.2',  reason: 'Too fast (7.2 min).' },
  { id: '6a29156d-cc17-7b7a-c947-4f85182160fc', dur: '8.0',  reason: 'Too fast (8.0 min).' },
  { id: '6a29155f-6c24-b4b7-959e-b8c8e505a3d2', dur: '7.9',  reason: 'Too fast (7.9 min).' },
  { id: '6a29155e-fc1c-2a48-a2e0-8d96edac5d23', dur: '5.7',  reason: 'Too fast (5.7 min). Open-text answers 1 character long.' },
  { id: '6a291536-e26f-34e2-3f06-a4e274cc4fa9', dur: '6.7',  reason: 'Too fast (6.7 min).' },
  { id: '6a2914da-3993-3813-cb9b-af6c24b1c44f', dur: '7.5',  reason: 'Too fast (7.5 min). Copy-paste: same answer for like and dislike (q75=q76).' },
  { id: '6a2914d2-78ba-f48b-38cf-a6d04fdb7a40', dur: '7.9',  reason: 'Too fast (7.9 min).' },
  { id: '6a2914b2-80ac-b2d7-2d5a-ceed97f7d576', dur: '18.5', reason: 'Open text too short (2 chars). Same answer used for like, dislike and brand questions.' },
];

const COL_ID  = 5400;
const COL_DUR = 900;
const COL_RSN = 3060;
const TABLE_W = COL_ID + COL_DUR + COL_RSN;

const headerRow = new TableRow({
  tableHeader: true,
  children: [
    hdrCell('Respondent ID', COL_ID),
    hdrCell('Min', COL_DUR),
    hdrCell('Reason for elimination', COL_RSN),
  ]
});

const dataRows = eliminate.map((e, i) => {
  const shade = i % 2 === 0 ? 'FFFFFF' : 'F2F2F2';
  return new TableRow({
    children: [
      dataCell(e.id,  COL_ID,  shade),
      dataCell(e.dur, COL_DUR, shade),
      reasonCell(e.reason, COL_RSN, shade),
    ]
  });
});

const doc = new Document({
  sections: [{
    properties: {
      page: {
        size: { width: 16838, height: 11906 },   // A4 landscape
        margin: { top: 720, right: 720, bottom: 720, left: 720 },
      }
    },
    children: [
      new Paragraph({
        children: [new TextRun({ text: 'Selmark Survey QC — Respondents to Eliminate', bold: true, font: 'Arial', size: 28, color: '1F3864' })]
      }),
      new Paragraph({
        children: [new TextRun({ text: 'Source: selmark_respuestas_2026-06-12  |  Rules: < 8 min, straight-lining, invalid demographics, copy-paste, poor open text  |  Total: ' + eliminate.length + ' respondents', font: 'Arial', size: 16, color: '666666' })]
      }),
      new Paragraph({ children: [new TextRun('')] }),
      new Table({
        width: { size: TABLE_W, type: WidthType.DXA },
        columnWidths: [COL_ID, COL_DUR, COL_RSN],
        rows: [headerRow, ...dataRows],
      }),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync('C:\\Users\\ajulve\\Downloads\\Fallos_v3.docx', buf);
  console.log('Done: Fallos_v3.docx (' + eliminate.length + ' rows)');
});
