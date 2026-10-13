const fs = require('fs');

let c = fs.readFileSync('backend/start.py', 'utf8');

const regex = /elif category == 'engine':/;
const interiorLogic = `elif category == 'interior':
        import re, os
        interior_rpos = []
        try:
            mod_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'views', 'partials', 'modules.js')
            with open(mod_path, 'r', encoding='utf-8') as f:
                content = f.read()
            match = re.search(r'const intColor\\s*=\\s*\\{([\\s\\S]*?)\\};', content)
            if match:
                interior_rpos = re.findall(r'"([A-Z0-9]+)"\\s*:', match.group(1))
        except Exception as e:
            print('Error parsing modules.js', e)
            
        rpo_list_str = "'" + "','".join(interior_rpos) + "'" if interior_rpos else "''"
        
        # If where_clause is empty, we must start it with WHERE instead of AND
        rpo_where = f" AND opt.rpo_code IN ({rpo_list_str})"
        if not where_clause:
            rpo_where = f"WHERE opt.rpo_code IN ({rpo_list_str})"

        sqlStatement = f"""
            WITH InteriorCounts AS (
                SELECT
                    opt.rpo_code AS rpo_code,
                    COUNT(*) AS total_count
                FROM Vehicles v
                JOIN Options opt ON v.vehicle_id = opt.vehicle_id
                {join_clause}
                {where_clause}
                {rpo_where}
                GROUP BY opt.rpo_code
            ),
            Ranked AS (
                SELECT
                    DENSE_RANK() OVER (ORDER BY total_count DESC) AS \`rank\`,
                    rpo_code AS label,
                    rpo_code,
                    total_count,
                    '' AS color_names,
                    ROUND(100.0 * total_count / SUM(total_count) OVER (), 5) AS percent
                FROM InteriorCounts
            )
            SELECT * FROM Ranked;
        """
    elif category == 'engine':`;

c = c.replace(regex, interiorLogic);
fs.writeFileSync('backend/start.py', c, 'utf8');
