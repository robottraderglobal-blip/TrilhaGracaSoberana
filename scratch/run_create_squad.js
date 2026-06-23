const { SquadGenerator } = require('../.aiox-core/development/scripts/squad');

async function main() {
  const generator = new SquadGenerator();
  const blueprintPath = 'c:\\Users\\ryzen\\Downloads\\Antigravity\\TrilhaGracaSoberana\\squads\\.designs\\devotional-enrichment-squad-design.yaml';
  
  const result = await generator.generateFromBlueprint(blueprintPath, { force: true });
  console.log('Squad generated successfully!');
  console.log('Location:', result.path);
  console.log('Files generated:', result.files.join('\n'));
}

main().catch(err => {
  console.error('Error generating squad:', err);
  process.exit(1);
});
