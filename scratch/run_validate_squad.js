const { SquadValidator } = require('../.aiox-core/development/scripts/squad');

async function main() {
  const validator = new SquadValidator({ verbose: true });
  const squadPath = 'c:\\Users\\ryzen\\Downloads\\Antigravity\\TrilhaGracaSoberana\\squads\\devotional-enrichment-squad';
  
  const result = await validator.validate(squadPath);
  console.log(validator.formatResult(result, squadPath));
  process.exit(result.valid ? 0 : 1);
}

main().catch(err => {
  console.error('Error validating squad:', err);
  process.exit(1);
});
