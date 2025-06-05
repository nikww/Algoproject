from django.core.management.base import BaseCommand
from algosite.models import Topic

class Command(BaseCommand):


    def handle(self, *args, **options):
        exercise_render_code = """
<div>
  <h3 id="task-instruction"></h3>
  <svg id="graph" width="600" height="600" style="border:1px solid #ccc;"></svg>
  <input id="answer-input" type="number" placeholder="Введите номер вершины" />
  <button id="check-btn">Проверить</button>
  <p id="feedback"></p>
</div>
"""

        exercise_logic_code = """
(() => {
    function generateExercise() {
        const n = Math.floor(Math.random() * 7) + 4;
        const edges = [];
        for(let i=1; i<n; i++) {
            edges.push([Math.floor(Math.random() * i), i]);
        }

        const LOG = 15;
        const adj = Array.from({length: n}, () => []);
        edges.forEach(([u, v]) => {
            adj[u].push(v);
            adj[v].push(u);
        });

        const up = Array.from({length: n}, () => new Array(LOG).fill(-1));
        const depth = new Array(n).fill(-1);
        depth[0] = 0;

        function dfs(v, p) {
            up[v][0] = p;
            for(let i=1; i<LOG; i++) {
                if(up[v][i-1] !== -1) {
                    up[v][i] = up[up[v][i-1]][i-1];
                }
            }
            adj[v].forEach(u => {
                if(u !== p) {
                    depth[u] = depth[v] + 1;
                    dfs(u, v);
                }
            });
        }
        dfs(0, -1);

        function lca(a, b) {
            if(depth[a] < depth[b]) [a, b] = [b, a];
            let diff = depth[a] - depth[b];
            for(let i=0; i<LOG; i++){
                if((diff & (1 << i)) !== 0){
                    a = up[a][i];
                }
            }
            if(a === b) return a;
            for(let i=LOG-1; i>=0; i--){
                if(up[a][i] !== -1 && up[a][i] !== up[b][i]){
                    a = up[a][i];
                    b = up[b][i];
                }
            }
            return up[a][0];
        }

        const svg = document.getElementById('graph');
        const width = svg.clientWidth || 600;
        const height = svg.clientHeight || 400;
        const verticalSpacing = 80;
        const levelVertices = {};

        for(let i=0; i<n; i++){
            if(!levelVertices[depth[i]]){
                levelVertices[depth[i]] = [];
            }
            levelVertices[depth[i]].push(i);
        }

        const positions = [];
        const levelCount = Object.keys(levelVertices).length;

        for(let level=0; level<levelCount; level++){
            const nodes = levelVertices[level];
            const count = nodes.length;
            const horizontalSpacing = width / (count + 1);
            for(let i=0; i<count; i++){
                const x = horizontalSpacing * (i + 1);
                const y = verticalSpacing * (level + 1);
                positions[nodes[i]] = {x, y};
            }
        }

        while(svg.firstChild) svg.removeChild(svg.firstChild);

        edges.forEach(([u, v]) => {
            const line = document.createElementNS("http://www.w3.org/2000/svg","line");
            line.setAttribute("x1", positions[u].x);
            line.setAttribute("y1", positions[u].y);
            line.setAttribute("x2", positions[v].x);
            line.setAttribute("y2", positions[v].y);
            line.setAttribute("stroke", "#555");
            line.setAttribute("stroke-width", 2);
            svg.appendChild(line);
        });

        positions.forEach(({x, y}, i) => {
            const circle = document.createElementNS("http://www.w3.org/2000/svg","circle");
            circle.setAttribute("cx", x);
            circle.setAttribute("cy", y);
            circle.setAttribute("r", 20);
            circle.setAttribute("fill", "#3b49df");
            circle.setAttribute("stroke", "#1c2dab");
            circle.setAttribute("stroke-width", 2);
            svg.appendChild(circle);

            const text = document.createElementNS("http://www.w3.org/2000/svg","text");
            text.setAttribute("x", x);
            text.setAttribute("y", y + 6);
            text.setAttribute("fill", "white");
            text.setAttribute("font-family", "Arial, sans-serif");
            text.setAttribute("font-size", 14);
            text.setAttribute("font-weight", "bold");
            text.setAttribute("text-anchor", "middle");
            text.setAttribute("pointer-events", "none");
            text.textContent = i;
            svg.appendChild(text);
        });

        const v1 = Math.floor(Math.random() * n);
        let v2;
        do { v2 = Math.floor(Math.random() * n); } while(v2 === v1);

        document.getElementById('task-instruction').textContent = `Найдите LCA для вершин ${v1} и ${v2}`;

        const correctLCA = lca(v1, v2);

        document.getElementById('check-btn').onclick = () => {
            const userAnswer = parseInt(document.getElementById('answer-input').value);
            const feedback = document.getElementById('feedback');
            if (isNaN(userAnswer)) {
                feedback.textContent = "Пожалуйста, введите номер вершины.";
                feedback.style.color = "red";
                return;
            }
            if (userAnswer === correctLCA) {
                feedback.textContent = "Верно! Отлично!";
                feedback.style.color = "green";

                generateExercise();
            } else {
                feedback.textContent = "Неверно, попробуйте ещё раз.";
                feedback.style.color = "red";
            }
        };
    }
    generateExercise();
})();
"""

        topic, created = Topic.objects.update_or_create(
            slug='lca',
            defaults={
                'title': 'LCA (Нижний общий предок)',
                'explanation': 'Ниже представлена визуализация задачи на нахождение LCA в случайном дереве.',
                'example_code': 'Пример кода на C++ для LCA...',
                'exercise_render_code': exercise_render_code,
                'exercise_logic_code': exercise_logic_code,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Тема "{topic.title}" успешно создана.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Тема "{topic.title}" успешно обновлена.'))
