from flask import Blueprint, jsonify, request, g
from app.models import Project, ProjectCategory

api_bp = Blueprint("api", __name__)


@api_bp.route("/projects")
def projects_filter():
    """AJAX endpoint for portfolio filtering."""
    category = request.args.get("category", "all")
    query = Project.query.filter_by(is_published=True)
    if category and category != "all":
        cat = ProjectCategory.query.filter_by(slug=category).first()
        if cat:
            query = query.filter_by(category_id=cat.id)
    projects = query.order_by(Project.display_order).all()
    lang = g.lang if hasattr(g, "lang") else "en"
    data = []
    for p in projects:
        data.append(
            {
                "id": p.id,
                "title": p.title,
                "slug": p.slug,
                "description": p.get_description(lang),
                "cover_image": p.cover_image,
                "category": p.category.get_name(lang) if p.category else "",
                "client": p.client or "",
                "url": f"/work/{p.slug}",
            }
        )
    return jsonify({"projects": data})
