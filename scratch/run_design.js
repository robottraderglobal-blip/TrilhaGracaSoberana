const { SquadDesigner } = require('../.aiox-core/development/scripts/squad');

async function main() {
  const designer = new SquadDesigner();
  const docPath = 'c:\\Users\\ryzen\\Downloads\\Antigravity\\TrilhaGracaSoberana\\novos\\serie3-aconselhamento-biblico-21-devocionais.md';
  const docs = await designer.collectDocumentation({
    docs: docPath,
    domain: 'devotional-enrichment'
  });
  
  const analysis = await designer.analyzeDomain(docs);
  
  const recommendations = {
    agents: [
      {
        id: 'exegete-researcher',
        role: 'Conducts theological exegesis, extracts Hebrew/Greek roots, matches biblical cross-references, and provides historical context for the passage.',
        commands: ['research-theology', 'lookup-roots'],
        confidence: 0.95,
        user_added: false,
        user_modified: false
      },
      {
        id: 'ryle-writer',
        role: 'Rewrites and expands the parsed devotionals into a highly detailed, solemn J.C. Ryle style, integrating the exegesis findings, using direct personal appeals ("Leitor..."), and adding rigorous pastoral application.',
        commands: ['write-devotional', 'expand-pastoral-application'],
        confidence: 0.92,
        user_added: false,
        user_modified: false
      },
      {
        id: 'theological-qa',
        role: 'Reviews and validates the enriched devotionals, checking for theological accuracy (Reformed orthodoxy), correctness of biblical references, stylistic alignment, and assigning a compliance/depth score.',
        commands: ['validate-depth', 'score-theology'],
        confidence: 0.9,
        user_added: false,
        user_modified: false
      }
    ],
    tasks: [
      {
        name: 'research-theology',
        agent: 'exegete-researcher',
        entrada: ['passage_reference', 'context_text'],
        saida: ['exegesis_notes', 'hebrew_greek_roots'],
        confidence: 0.95
      },
      {
        name: 'write-devotional',
        agent: 'ryle-writer',
        entrada: ['raw_devotional_text', 'exegesis_notes', 'hebrew_greek_roots'],
        saida: ['enriched_devotional_text'],
        confidence: 0.92
      },
      {
        name: 'validate-depth',
        agent: 'theological-qa',
        entrada: ['enriched_devotional_text'],
        saida: ['evaluation_score', 'feedback_notes', 'passed'],
        confidence: 0.9
      }
    ]
  };

  const blueprint = designer.generateBlueprint({
    analysis,
    recommendations,
    metadata: {
      source_docs: [docPath],
      created_at: new Date().toISOString()
    }
  });

  const savePath = await designer.saveBlueprint(blueprint, 'c:\\Users\\ryzen\\Downloads\\Antigravity\\TrilhaGracaSoberana\\squads\\.designs', { force: true });
  console.log('Saved blueprint successfully to:', savePath);
}

main().catch(err => {
  console.error('Error designing squad:', err);
  process.exit(1);
});
