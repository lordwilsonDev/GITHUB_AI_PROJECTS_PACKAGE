// mon_cli.cjs - tiny CLI wrapper
const { answerMonitorQuestion } = require("./mon_router.cjs");

const question = process.argv.slice(2).join(" ") || "overall health";
const out = answerMonitorQuestion(question);
console.log(out);
