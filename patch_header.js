const fs = require('fs');
let c = fs.readFileSync('frontend/views/partials/header.ejs', 'utf8');
c = c.replace(
    '<li class="mb-2 mt-2 i-link"><a href="/stats?category=color" class="text-decoration-none text-light d-flex align-items-center" style="font-size: 1.05rem;">Colors</a></li>',
    `<li class="mb-2 mt-2 i-link"><a href="/stats?category=color" class="text-decoration-none text-light d-flex align-items-center" style="font-size: 1.05rem;">Exterior Colors</a></li>
                            <li class="mb-2 mt-2 i-link"><a href="/stats?category=interior" class="text-decoration-none text-light d-flex align-items-center" style="font-size: 1.05rem;">Interior Colors</a></li>`
);
fs.writeFileSync('frontend/views/partials/header.ejs', c, 'utf8');
