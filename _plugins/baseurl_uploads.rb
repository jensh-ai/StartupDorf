# Beiträge enthalten wurzel-relative Pfade wie "/assets/uploads/...".
# Läuft die Seite unter einem Unterpfad (z. B. Vorschau auf github.io/StartupDorf/),
# wird hier die baseurl davorgesetzt. Mit eigener Domain (baseurl leer) passiert nichts.
# Erfasst Attribute mit doppelten und einfachen Anführungszeichen (href='…' aus WordPress)
# sowie CSS url(…).
UPLOADS_PATTERN = %r{(=\s*["']|url\(\s*["']?)/assets/uploads/}

Jekyll::Hooks.register [:posts, :documents, :pages], :post_render do |doc|
  base = doc.site.config["baseurl"].to_s.chomp("/")
  next if base.empty? || doc.output.nil?
  doc.output = doc.output.gsub(UPLOADS_PATTERN) { "#{$1}#{base}/assets/uploads/" }
end
