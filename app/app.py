from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
from .models import db, LabMember, Faculty, Student, Collaborator, Project, Equipment, EquipmentUse, Publication, Authorship, GrantFund, ProjectGrant, WorksOn, Mentorship
from datetime import datetime, date
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from typing import Optional
import re

def _parse_date(s: Optional[str]):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s).date()
    except Exception:
        return None

def _parse_datetime(s: Optional[str]):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'labmanager.db')

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    def _get_next_id(prefix, model, id_attr):
        q = model.query.filter(getattr(model, id_attr).like(f"{prefix}%")).all()
        max_n = 0
        for row in q:
            val = getattr(row, id_attr)
            if val and val.startswith(prefix):
                suf = val[len(prefix):]
                if suf.isdigit():
                    n = int(suf)
                    if n > max_n:
                        max_n = n
        return f"{prefix}{max_n+1}"

    # Compatibility helpers (used by DF routes)
    def next_member_id(member_type):
        prefix = {'faculty': 'F', 'student': 'S', 'collaborator': 'O'}.get(member_type, 'O')
        return _get_next_id(prefix, LabMember, 'member_id')

    def next_project_id():
        return _get_next_id('P', Project, 'project_id')

    def next_grant_id():
        return _get_next_id('G', GrantFund, 'grant_id')

    def next_equip_id():
        return _get_next_id('E', Equipment, 'equip_id')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/favicon.ico')
    def favicon():
        try:
            return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
        except Exception:
            return ('', 204)

    @app.route('/members')
    def members():
        members = LabMember.query.order_by(LabMember.member_id).all()
        return render_template('members.html', members=members)

    @app.route('/projects')
    def projects():
        projects = Project.query.order_by(Project.project_id).all()
        return render_template('projects.html', projects=projects)

    @app.route('/pm')
    def project_member_dashboard():
        return render_template('project_member_dashboard.html')

    @app.route('/reports_dashboard')
    def reports_dashboard():
        return render_template('grant_publication_dashboard.html')

    @app.route('/pm/project_status')
    def pm_project_status():
        # support optional search by project_id (GET param `project_id`)
        pid = request.args.get('project_id')
        project = None
        grants = []
        members = []
        mentorships = []
        if pid:
            # accept either numeric id or prefixed id like P1
            search_id = pid.strip()
            if not search_id.startswith('P') and search_id.isdigit():
                search_id = f'P{search_id}'
            project = db.session.get(Project, search_id)
            if project:
                # related grants
                grants = db.session.query(ProjectGrant, GrantFund).join(GrantFund, ProjectGrant.grant_id==GrantFund.grant_id).filter(ProjectGrant.project_id==project.project_id).all()
                # members working on project
                members = db.session.query(WorksOn, LabMember).join(LabMember, WorksOn.member_id==LabMember.member_id).filter(WorksOn.project_id==project.project_id).all()
                # mentorships where both mentor and mentee work on the same project
                mentorships = []
                try:
                    member_ids = {m.member_id for wo, m in members}
                    if member_ids:
                        ms = Mentorship.query.filter(Mentorship.mentor_id.in_(member_ids), Mentorship.mentee_id.in_(member_ids)).all()
                        for mt in ms:
                            try:
                                mentor = db.session.get(LabMember, mt.mentor_id)
                            except Exception:
                                mentor = None
                            try:
                                mentee = db.session.get(LabMember, mt.mentee_id)
                            except Exception:
                                mentee = None
                            mentorships.append({'mentor': mentor, 'mentee': mentee, 'start_date': mt.start_date, 'end_date': mt.end_date, 'notes': mt.notes})
                except Exception:
                    mentorships = []
        return render_template('project_status.html', project=project, grants=grants, members=members, mentorships=mentorships)

    @app.route('/project/status')
    def project_status():
        pid = request.args.get('project_id')
        when = request.args.get('when')
        when_dt = _parse_datetime(when) if when else datetime.now()
        if pid and not pid.startswith('P') and pid.isdigit():
            pid = f'P{pid}'
        p = db.session.get(Project, pid) if pid else None
        if not p:
            return jsonify({'project_id': pid, 'status': 'not found', 'active': False})
        # compute whether active at `when_dt` (if within start/end and status=='active')
        active = False
        try:
            sd = p.start_date
            ed = p.end_date
            if sd and when_dt.date() < sd:
                active = False
            else:
                if ed is None:
                    active = (p.status == 'active')
                else:
                    active = (when_dt.date() >= sd and when_dt.date() <= ed and p.status == 'active')
        except Exception:
            active = (p.status == 'active')
        return jsonify({'project_id': p.project_id, 'status': p.status, 'active': bool(active)})

    @app.route('/pm/mentorship_relations')
    def pm_mentorship_relations():
        # Render the same mentorship listing as /view/mentorship so content matches
        mentorships = Mentorship.query.order_by(Mentorship.mentor_id).all()
        for m in mentorships:
            try:
                m.mentor = db.session.get(LabMember, m.mentor_id)
            except Exception:
                m.mentor = None
            try:
                m.mentee = db.session.get(LabMember, m.mentee_id)
            except Exception:
                m.mentee = None
        return render_template('view_mentorship.html', mentorships=mentorships)

    # --- Project CRUD ---
    @app.route('/projects/new', methods=['GET', 'POST'])
    def project_new():
        faculties = Faculty.query.all()
        grants = GrantFund.query.order_by(GrantFund.grant_id).all()
        if request.method == 'POST':
            title = request.form.get('title')
            start_date = _parse_date(request.form.get('start_date') or None)
            end_date = _parse_date(request.form.get('end_date') or None)
            # validate dates
            if start_date and end_date and end_date < start_date:
                flash('Project end date cannot be before start date.', 'error')
                return redirect(url_for('project_new'))
            # compute expected duration in months if dates provided
            expected_duration = None
            if start_date and end_date:
                expected_duration = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            else:
                ed = request.form.get('expected_duration')
                if ed:
                    try:
                        expected_duration = int(ed)
                    except ValueError:
                        flash('Expected duration must be an integer number of months.', 'error')
                        return redirect(url_for('project_new'))
                else:
                    expected_duration = None
            # server-side required fields enforcement
            if not title or start_date is None or end_date is None or expected_duration is None:
                flash('Title, start date, end date and expected duration are required.', 'error')
                return redirect(url_for('project_new'))
            status = request.form.get('status')
            leader_id = request.form.get('leader_id') if request.form.get('leader_id') else None
            if not status or not leader_id:
                flash('Status and leader are required.', 'error')
                return redirect(url_for('project_new'))
            project_id = _get_next_id('P', Project, 'project_id')
            p = Project(project_id=project_id, title=title, start_date=start_date, end_date=end_date,
                        expected_duration=expected_duration, status=status, leader_id=leader_id)
            # validate grant allocations and prepare ProjectGrant rows
            grant_ids = request.form.getlist('grant_ids')
            pg_rows = []
            try:
                for gid in grant_ids:
                    if not gid:
                        continue
                    amt_raw = request.form.get(f'amount_{gid}')
                    if amt_raw is None or amt_raw.strip() == '':
                        flash(f'Allocation amount required for grant {gid}.', 'error')
                        return redirect(url_for('project_new'))
                    try:
                        amt = float(amt_raw)
                    except Exception:
                        flash(f'Allocation amount for grant {gid} must be numeric.', 'error')
                        return redirect(url_for('project_new'))
                    if amt < 0:
                        flash(f'Allocation amount for grant {gid} must be non-negative.', 'error')
                        return redirect(url_for('project_new'))
                    # check against grant budget
                    grant = db.session.get(GrantFund, gid)
                    if grant and grant.budget is not None:
                        # sum existing allocations for this grant
                        existing = ProjectGrant.query.filter_by(grant_id=gid).all()
                        existing_sum = sum([pg.amount_allocated or 0 for pg in existing])
                        new_total = existing_sum + amt
                        if new_total > grant.budget:
                            flash(f'Allocation for grant {gid} would exceed its budget (budget={grant.budget}, would be {new_total}).', 'error')
                            return redirect(url_for('project_new'))
                    pg_rows.append((gid, amt))
                # all validations passed; persist project and ProjectGrant rows
                db.session.add(p)
                for gid, amt in pg_rows:
                    pg = ProjectGrant(project_id=p.project_id, grant_id=gid, amount_allocated=amt)
                    db.session.add(pg)
                db.session.commit()
                # ensure leader is recorded in WorksOn as leader
                try:
                    if leader_id:
                        existing_leader = WorksOn.query.filter_by(member_id=leader_id, project_id=p.project_id).first()
                        if not existing_leader:
                            w = WorksOn(member_id=leader_id, project_id=p.project_id, role='leader', weekly_hours=10)
                            db.session.add(w)
                            db.session.commit()
                except Exception:
                    db.session.rollback()
            except Exception as ex:
                db.session.rollback()
                flash(f'Error creating project: {ex}', 'error')
                return redirect(url_for('project_new'))
            return redirect(url_for('projects'))
        return render_template('project_form.html', project=None, faculties=faculties, grants=grants, project_grant_amounts={})

    @app.route('/projects/<pid>/edit', methods=['GET', 'POST'])
    def project_edit(pid):
        p = Project.query.get_or_404(pid)
        faculties = Faculty.query.all()
        grants = GrantFund.query.order_by(GrantFund.grant_id).all()
        if request.method == 'POST':
            p.title = request.form.get('title')
            p.start_date = _parse_date(request.form.get('start_date') or None)
            p.end_date = _parse_date(request.form.get('end_date') or None)
            # validate dates
            if p.start_date and p.end_date and p.end_date < p.start_date:
                flash('Project end date cannot be before start date.', 'error')
                return redirect(url_for('project_edit', pid=pid))
            # compute expected duration
            if p.start_date and p.end_date:
                p.expected_duration = (p.end_date.year - p.start_date.year) * 12 + (p.end_date.month - p.start_date.month)
            else:
                ed = request.form.get('expected_duration')
                if ed:
                    try:
                        p.expected_duration = int(ed)
                    except ValueError:
                        flash('Expected duration must be an integer number of months.', 'error')
                        return redirect(url_for('project_edit', pid=pid))
                else:
                    p.expected_duration = None
            # enforce required fields
            if not p.title or p.start_date is None or p.end_date is None or p.expected_duration is None:
                flash('Title, start date, end date and expected duration are required.', 'error')
                return redirect(url_for('project_edit', pid=pid))
            p.status = request.form.get('status')
            # capture old leader before changing
            old_leader = p.leader_id
            p.leader_id = request.form.get('leader_id') if request.form.get('leader_id') else None
            if not p.status or not p.leader_id:
                flash('Status and leader are required.', 'error')
                return redirect(url_for('project_edit', pid=pid))
            try:
                # validate allocations first
                selected = set(request.form.getlist('grant_ids'))
                # prepare amounts for selected grants
                sel_amounts = {}
                for gid in selected:
                    if not gid:
                        continue
                    amt_raw = request.form.get(f'amount_{gid}')
                    if amt_raw is None or amt_raw.strip() == '':
                        flash(f'Allocation amount required for grant {gid}.', 'error')
                        return redirect(url_for('project_edit', pid=pid))
                    try:
                        amt = float(amt_raw)
                    except Exception:
                        flash(f'Allocation amount for grant {gid} must be numeric.', 'error')
                        return redirect(url_for('project_edit', pid=pid))
                    if amt < 0:
                        flash(f'Allocation amount for grant {gid} must be non-negative.', 'error')
                        return redirect(url_for('project_edit', pid=pid))
                    # check against grant budget: sum of allocations excluding this project
                    grant = db.session.get(GrantFund, gid)
                    if grant and grant.budget is not None:
                        existing = ProjectGrant.query.filter_by(grant_id=gid).all()
                        existing_sum = sum([pg.amount_allocated or 0 for pg in existing if pg.project_id != p.project_id])
                        new_total = existing_sum + amt
                        if new_total > grant.budget:
                            flash(f'Allocation for grant {gid} would exceed its budget (budget={grant.budget}, would be {new_total}).', 'error')
                            return redirect(url_for('project_edit', pid=pid))
                    sel_amounts[gid] = amt
                # persist base project changes
                db.session.commit()
                # synchronize ProjectGrant rows
                existing = {pg.grant_id: pg for pg in ProjectGrant.query.filter_by(project_id=p.project_id).all()}
                # remove unselected
                for gid, pg in existing.items():
                    if gid not in selected:
                        try:
                            db.session.delete(pg)
                        except Exception:
                            db.session.rollback()
                # add/update selected
                for gid in selected:
                    if gid in existing:
                        ew = existing[gid]
                        ew.amount_allocated = sel_amounts.get(gid)
                    else:
                        newpg = ProjectGrant(project_id=p.project_id, grant_id=gid, amount_allocated=sel_amounts.get(gid))
                        db.session.add(newpg)
                db.session.commit()
            except Exception as ex:
                db.session.rollback()
                flash(f'Error updating project: {ex}', 'error')
                return redirect(url_for('project_edit', pid=pid))
            return redirect(url_for('projects'))
        # prepare selected grant ids for template
        project_grants = ProjectGrant.query.filter_by(project_id=p.project_id).all()
        project_grant_ids = [pg.grant_id for pg in project_grants]
        project_grant_amounts = {pg.grant_id: (pg.amount_allocated if pg.amount_allocated is not None else '') for pg in project_grants}
        return render_template('project_form.html', project=p, faculties=faculties, grants=grants, project_grant_ids=project_grant_ids, project_grant_amounts=project_grant_amounts)

    @app.route('/projects/<pid>/delete', methods=['POST'])
    def project_delete(pid):
        p = Project.query.get_or_404(pid)
        try:
            # remove dependent association rows first
            ProjectGrant.query.filter_by(project_id=p.project_id).delete(synchronize_session=False)
            WorksOn.query.filter_by(project_id=p.project_id).delete(synchronize_session=False)
            db.session.delete(p)
            db.session.commit()
            flash(f'Project {p.project_id} and related records deleted.', 'success')
        except Exception as ex:
            db.session.rollback()
            flash(f'Error deleting project: {ex}', 'error')
        return redirect(url_for('projects'))

    @app.route('/equipment')
    def equipment():
        equipment = Equipment.query.order_by(Equipment.equip_id).all()
        return render_template('equipment.html', equipment=equipment)

    # --- Equipment CRUD ---
    @app.route('/equipment/new', methods=['GET', 'POST'])
    def equipment_new():
        if request.method == 'POST':
            name = request.form.get('name')
            type_ = request.form.get('type')
            purchase_date = _parse_date(request.form.get('purchase_date') or None)
            status = request.form.get('status')
            location = request.form.get('location')
            notes = request.form.get('notes')
            # server-side validation: all fields required
            if not (name and type_ and purchase_date and status and location and notes):
                flash('All equipment fields are required.', 'error')
                return redirect(url_for('equipment_new'))
            equip_id = _get_next_id('E', Equipment, 'equip_id')
            e = Equipment(equip_id=equip_id, name=name, type=type_, purchase_date=purchase_date, status=status, location=location, notes=notes)
            try:
                db.session.add(e)
                db.session.commit()
            except Exception as ex:
                db.session.rollback()
                flash(f'Error adding equipment: {ex}', 'error')
                return redirect(url_for('equipment_new'))
            return redirect(url_for('equipment'))
        return render_template('equipment_form.html', equipment=None)

    @app.route('/equipment/<eid>/edit', methods=['GET', 'POST'])
    def equipment_edit(eid):
        e = Equipment.query.get_or_404(eid)
        if request.method == 'POST':
            e.name = request.form.get('name')
            e.type = request.form.get('type')
            e.purchase_date = _parse_date(request.form.get('purchase_date') or None)
            e.status = request.form.get('status')
            e.location = request.form.get('location')
            e.notes = request.form.get('notes')
            db.session.commit()
            return redirect(url_for('equipment'))
        return render_template('equipment_form.html', equipment=e)

    @app.route('/equipment/<eid>/delete', methods=['POST'])
    def equipment_delete(eid):
        e = Equipment.query.get_or_404(eid)
        db.session.delete(e)
        db.session.commit()
        return redirect(url_for('equipment'))

    @app.route('/grants')
    def grants():
        grants = GrantFund.query.order_by(GrantFund.grant_id).all()
        return render_template('grants.html', grants=grants)

    @app.route('/grants/<string:gid>/edit', methods=['GET', 'POST'])
    def grant_edit(gid):
        g = GrantFund.query.get_or_404(gid)
        projects = Project.query.order_by(Project.project_id).all()
        if request.method == 'POST':
            source = request.form.get('source')
            budget = request.form.get('budget')
            start_date = _parse_date(request.form.get('start_date') or None)
            duration = request.form.get('duration')
            if not source:
                flash('Grant source is required.', 'error')
                return redirect(url_for('grant_edit', gid=gid))
            try:
                budget_f = float(budget) if budget else None
            except Exception:
                flash('Budget must be numeric.', 'error')
                return redirect(url_for('grant_edit', gid=gid))
            try:
                duration_i = int(duration) if duration else None
            except Exception:
                flash('Duration must be an integer number of months.', 'error')
                return redirect(url_for('grant_edit', gid=gid))
            project_ids = request.form.getlist('project_ids')
            if not project_ids:
                flash('A grant must be assigned to at least one project.', 'error')
                return redirect(url_for('grant_edit', gid=gid))
            # validate allocations
            allocs = []
            try:
                total_alloc = 0.0
                for pid in project_ids:
                    amt_raw = request.form.get(f'amount_{pid}')
                    if amt_raw is None or amt_raw.strip() == '':
                        flash(f'Allocation amount required for project {pid}.', 'error')
                        return redirect(url_for('grant_edit', gid=gid))
                    try:
                        amt = float(amt_raw)
                    except Exception:
                        flash(f'Allocation for project {pid} must be numeric.', 'error')
                        return redirect(url_for('grant_edit', gid=gid))
                    if amt < 0:
                        flash(f'Allocation for project {pid} must be non-negative.', 'error')
                        return redirect(url_for('grant_edit', gid=gid))
                    allocs.append((pid, amt))
                    total_alloc += amt
                if budget_f is not None and total_alloc > budget_f:
                    flash(f'Total allocation to projects ({total_alloc}) exceeds grant budget ({budget_f}).', 'error')
                    return redirect(url_for('grant_edit', gid=gid))
                # persist changes
                g.source = source
                g.budget = budget_f
                g.start_date = start_date
                g.duration = duration_i
                db.session.commit()
                # synchronize ProjectGrant rows
                existing = {pg.project_id: pg for pg in ProjectGrant.query.filter_by(grant_id=g.grant_id).all()}
                selected = set(project_ids)
                # remove unselected
                for pid, pg in existing.items():
                    if pid not in selected:
                        try:
                            db.session.delete(pg)
                        except Exception:
                            db.session.rollback()
                # add/update selected
                for pid, amt in allocs:
                    if pid in existing:
                        existing[pid].amount_allocated = amt
                    else:
                        newpg = ProjectGrant(project_id=pid, grant_id=g.grant_id, amount_allocated=amt)
                        db.session.add(newpg)
                db.session.commit()
                flash('Grant updated.', 'success')
                return redirect(url_for('grants'))
            except Exception as ex:
                db.session.rollback()
                flash(f'Error updating grant: {ex}', 'error')
                return redirect(url_for('grant_edit', gid=gid))
        # prepare selected project ids and amounts
        project_grants = ProjectGrant.query.filter_by(grant_id=g.grant_id).all()
        selected_ids = [pg.project_id for pg in project_grants]
        amounts = {pg.project_id: (pg.amount_allocated if pg.amount_allocated is not None else '') for pg in project_grants}
        return render_template('grant_form.html', grant=g, projects=projects, selected_ids=selected_ids, amounts=amounts)

    @app.route('/grants/<string:gid>/delete', methods=['POST'])
    def grant_delete(gid):
        g = GrantFund.query.get_or_404(gid)
        try:
            # remove related ProjectGrant rows first
            ProjectGrant.query.filter_by(grant_id=gid).delete()
            db.session.delete(g)
            db.session.commit()
            flash('Grant deleted.', 'success')
        except Exception as ex:
            db.session.rollback()
            flash(f'Error deleting grant: {ex}', 'error')
        return redirect(url_for('grants'))

    @app.route('/grants/new', methods=['GET', 'POST'])
    def grant_new():
        projects = Project.query.order_by(Project.project_id).all()
        if request.method == 'POST':
            source = request.form.get('source')
            budget = request.form.get('budget')
            start_date = _parse_date(request.form.get('start_date') or None)
            duration = request.form.get('duration')
            # basic validation
            if not source:
                flash('Grant source is required.', 'error')
                return redirect(url_for('grant_new'))
            try:
                budget_f = float(budget) if budget else None
            except Exception:
                flash('Budget must be numeric.', 'error')
                return redirect(url_for('grant_new'))
            try:
                duration_i = int(duration) if duration else None
            except Exception:
                flash('Duration must be an integer number of months.', 'error')
                return redirect(url_for('grant_new'))
            project_ids = request.form.getlist('project_ids')
            if not project_ids:
                flash('A grant must be assigned to at least one project.', 'error')
                return redirect(url_for('grant_new'))
            # validate per-project allocations and ensure total <= budget
            allocs = []
            try:
                total_alloc = 0.0
                for pid in project_ids:
                    amt_raw = request.form.get(f'amount_{pid}')
                    if amt_raw is None or amt_raw.strip() == '':
                        flash(f'Allocation amount required for project {pid}.', 'error')
                        return redirect(url_for('grant_new'))
                    try:
                        amt = float(amt_raw)
                    except Exception:
                        flash(f'Allocation for project {pid} must be numeric.', 'error')
                        return redirect(url_for('grant_new'))
                    if amt < 0:
                        flash(f'Allocation for project {pid} must be non-negative.', 'error')
                        return redirect(url_for('grant_new'))
                    allocs.append((pid, amt))
                    total_alloc += amt
                if budget_f is not None and total_alloc > budget_f:
                    flash(f'Total allocation to projects ({total_alloc}) exceeds grant budget ({budget_f}).', 'error')
                    return redirect(url_for('grant_new'))
                # create grant and ProjectGrant rows
                gid = _get_next_id('G', GrantFund, 'grant_id')
                g = GrantFund(grant_id=gid, source=source, budget=budget_f, start_date=start_date, duration=duration_i)
                db.session.add(g)
                for pid, amt in allocs:
                    pg = ProjectGrant(project_id=pid, grant_id=gid, amount_allocated=amt)
                    db.session.add(pg)
                db.session.commit()
                flash('Grant created and assigned to projects.', 'success')
                return redirect(url_for('grants'))
            except Exception as ex:
                db.session.rollback()
                flash(f'Error creating grant: {ex}', 'error')
                return redirect(url_for('grant_new'))
        return render_template('grant_form.html', grant=None, projects=projects)

    @app.route('/publications')
    def publications():
        pubs = Publication.query.order_by(Publication.pub_id).all()
        return render_template('publications.html', pubs=pubs)

    @app.route('/publications/new', methods=['GET', 'POST'])
    def publication_new():
        members = LabMember.query.order_by(LabMember.member_id).all()
        if request.method == 'POST':
            title = request.form.get('title')
            pub_date = _parse_date(request.form.get('pub_date') or None)
            venue = request.form.get('venue')
            doi = request.form.get('doi')
            status = request.form.get('status')
            primary = request.form.get('primary_author')
            co_authors = request.form.getlist('co_authors')
            if not title:
                flash('Title is required.', 'error')
                return redirect(url_for('publication_new'))
            if not primary:
                flash('A primary author (at least one lab member) is required.', 'error')
                return redirect(url_for('publication_new'))
            # ensure primary is included in authors list
            if primary not in co_authors:
                co_authors.insert(0, primary)
            pid = _get_next_id('B', Publication, 'pub_id')
            p = Publication(pub_id=pid, title=title, pub_date=pub_date, venue=venue, doi=doi, status=status)
            try:
                db.session.add(p)
                # create authorship rows: primary first
                order = 1
                for mid in co_authors:
                    if not mid:
                        continue
                    role = 'primary' if mid == primary and order == 1 else None
                    a = Authorship(pub_id=pid, member_id=mid, author_order=order, author_role=role)
                    db.session.add(a)
                    order += 1
                db.session.commit()
                flash('Publication created with authors.', 'success')
                return redirect(url_for('publications'))
            except Exception as ex:
                db.session.rollback()
                flash(f'Error creating publication: {ex}', 'error')
                return redirect(url_for('publication_new'))
        return render_template('publication_form.html', publication=None, members=members)

    @app.route('/publications/<string:pid>/edit', methods=['GET', 'POST'])
    def publication_edit(pid):
        p = Publication.query.get_or_404(pid)
        members = LabMember.query.order_by(LabMember.member_id).all()
        # load existing authorship to prefill
        existing = Authorship.query.filter_by(pub_id=pid).order_by(Authorship.author_order).all()
        existing_ids = [a.member_id for a in existing]
        primary_id = None
        for a in existing:
            if a.author_role == 'primary':
                primary_id = a.member_id
                break
        if not primary_id and existing:
            primary_id = existing[0].member_id
        if request.method == 'POST':
            p.title = request.form.get('title')
            p.pub_date = _parse_date(request.form.get('pub_date') or None)
            p.venue = request.form.get('venue')
            p.doi = request.form.get('doi')
            p.status = request.form.get('status')
            primary = request.form.get('primary_author')
            co_authors = request.form.getlist('co_authors')
            if not primary:
                flash('A primary author (at least one lab member) is required.', 'error')
                return redirect(url_for('publication_edit', pid=pid))
            if primary not in co_authors:
                co_authors.insert(0, primary)
            try:
                # remove existing authorship rows and recreate
                Authorship.query.filter_by(pub_id=pid).delete()
                order = 1
                for mid in co_authors:
                    if not mid:
                        continue
                    role = 'primary' if mid == primary and order == 1 else None
                    a = Authorship(pub_id=pid, member_id=mid, author_order=order, author_role=role)
                    db.session.add(a)
                    order += 1
                db.session.commit()
                flash('Publication updated.', 'success')
                return redirect(url_for('publications'))
            except Exception as ex:
                db.session.rollback()
                flash(f'Error updating publication: {ex}', 'error')
                return redirect(url_for('publication_edit', pid=pid))
        return render_template('publication_form.html', publication=p, members=members, existing_ids=existing_ids, primary_id=primary_id)

    @app.route('/publications/<string:pid>/delete', methods=['POST'])
    def publication_delete(pid):
        p = Publication.query.get_or_404(pid)
        try:
            # remove related authorship rows first
            Authorship.query.filter_by(pub_id=pid).delete()
            db.session.delete(p)
            db.session.commit()
            flash('Publication deleted.', 'success')
        except Exception as ex:
            db.session.rollback()
            flash(f'Error deleting publication: {ex}', 'error')
        return redirect(url_for('publications'))

    # --- Member CRUD ---
    @app.route('/members/new', methods=['GET', 'POST'])
    def member_new():
        projects = Project.query.order_by(Project.project_id).all()
        if request.method == 'POST':
            name = request.form.get('name')
            member_type = request.form.get('member_type')
            join_date = _parse_date(request.form.get('join_date') or None)
            # default join_date to today if not provided so DB NOT NULL constraint is satisfied
            if join_date is None:
                join_date = datetime.today().date()
            # basic validation
            if not name or not member_type:
                flash('Name and member type are required.', 'error')
                return redirect(url_for('member_new'))
            # optional project assignments
            project_ids = request.form.getlist('project_ids')
            # validate role and weekly hours for each selected project
            work_items = []
            for pid in project_ids:
                role = (request.form.get(f'role_{pid}') or '').strip()
                wh = request.form.get(f'weekly_hours_{pid}')
                try:
                    whf = float(wh)
                except Exception:
                    flash(f'Weekly hours must be numeric for project {pid}.', 'error')
                    return redirect(url_for('member_new'))
                if not role:
                    flash(f'Role is required for project {pid}.', 'error')
                    return redirect(url_for('member_new'))
                work_items.append((pid, role, whf))
            try:
                # generate member_id with prefix by type
                prefix = 'F' if member_type == 'faculty' else ('S' if member_type == 'student' else 'O')
                mid = _get_next_id(prefix, LabMember, 'member_id')
                m = LabMember(member_id=mid, name=name, member_type=member_type, join_date=join_date)
                db.session.add(m)
                db.session.commit()
                # ensure leader is recorded in WorksOn (if not already)
                try:
                    if p.leader_id:
                        exist = WorksOn.query.filter_by(member_id=p.leader_id, project_id=p.project_id).first()
                        if exist:
                            # set role to leader and ensure default hours
                            exist.role = 'leader'
                            try:
                                if not exist.weekly_hours or float(exist.weekly_hours) == 0:
                                    exist.weekly_hours = 10
                            except Exception:
                                exist.weekly_hours = 10
                            db.session.commit()
                        else:
                            w = WorksOn(member_id=p.leader_id, project_id=p.project_id, role='leader', weekly_hours=10)
                            db.session.add(w)
                            db.session.commit()
                    # if leader changed, remove previous leader's leader-role entry
                    if 'old_leader' in locals() and old_leader and old_leader != p.leader_id:
                        try:
                            old = WorksOn.query.filter_by(member_id=old_leader, project_id=p.project_id, role='leader').first()
                            if old:
                                db.session.delete(old)
                                db.session.commit()
                        except Exception:
                            db.session.rollback()
                except Exception:
                    db.session.rollback()
                # create subtype if provided
                if member_type == 'faculty':
                    dept = request.form.get('department')
                    aff = request.form.get('faculty_affiliation')
                    title = request.form.get('title')
                    f = Faculty(member_id=m.member_id, department=dept, affiliation=aff, title=title)
                    db.session.add(f)
                    db.session.commit()
                elif member_type == 'student':
                    sid = request.form.get('student_number')
                    academic_level = request.form.get('academic_level')
                    major = request.form.get('major')
                    aff = request.form.get('student_affiliation')
                    s = Student(member_id=m.member_id, student_number=sid, academic_level=academic_level, major=major, affiliation=aff)
                    db.session.add(s)
                    db.session.commit()
                elif member_type == 'collaborator':
                    org = request.form.get('organization')
                    contact = request.form.get('contact_info')
                    bio = request.form.get('biography')
                    c = Collaborator(member_id=m.member_id, organization=org, contact_info=contact, biography=bio)
                    db.session.add(c)
                    db.session.commit()
                # create WorksOn entries for each selected project (if any)
                for pid, role, whf in work_items:
                    wo = WorksOn(member_id=m.member_id, project_id=pid, role=role, weekly_hours=whf)
                    db.session.add(wo)
                db.session.commit()
                flash('Member created successfully.', 'success')
                return redirect(url_for('members'))
            except Exception as ex:
                db.session.rollback()
                flash(f'Error creating member: {ex}', 'error')
                return redirect(url_for('member_new'))
        # pass an empty subtype dict so template can safely check subtype keys
        return render_template('member_form.html', member=None, subtype={}, projects=projects)

    @app.route('/members/<mid>/edit', methods=['GET', 'POST'])
    def member_edit(mid):
        m = LabMember.query.get_or_404(mid)
        # load subtype records if exist
        faculty = db.session.get(Faculty, mid)
        student = db.session.get(Student, mid)
        collaborator = db.session.get(Collaborator, mid)
        if request.method == 'POST':
            name = request.form.get('name')
            member_type = request.form.get('member_type')
            join_date = _parse_date(request.form.get('join_date') or None)
            if not name or not member_type:
                flash('Name and member type are required.', 'error')
                return redirect(url_for('member_edit', mid=mid))
            try:
                # update base
                m.name = name
                old_type = m.member_type
                m.member_type = member_type
                # only update join_date if provided in form
                if join_date is not None:
                    m.join_date = join_date
                db.session.commit()
                # handle subtype transitions
                # remove old subtype rows if type changed
                if old_type != member_type:
                    if faculty:
                        try:
                            db.session.delete(faculty)
                            db.session.commit()
                        except:
                            db.session.rollback()
                    if student:
                        try:
                            db.session.delete(student)
                            db.session.commit()
                        except:
                            db.session.rollback()
                    if collaborator:
                        try:
                            db.session.delete(collaborator)
                            db.session.commit()
                        except:
                            db.session.rollback()
                # create or update subtype data
                if member_type == 'faculty':
                    dept = request.form.get('department')
                    aff = request.form.get('faculty_affiliation')
                    title = request.form.get('title')
                    fac = db.session.get(Faculty, mid)
                    if fac:
                        fac.department = dept
                        fac.affiliation = aff
                        fac.title = title
                    else:
                        fac = Faculty(member_id=mid, department=dept, affiliation=aff, title=title)
                        db.session.add(fac)
                    db.session.commit()
                elif member_type == 'student':
                    sid = request.form.get('student_number')
                    academic_level = request.form.get('academic_level')
                    major = request.form.get('major')
                    aff = request.form.get('student_affiliation')
                    st = db.session.get(Student, mid)
                    if st:
                        st.student_number = sid
                        st.academic_level = academic_level
                        st.major = major
                        st.affiliation = aff
                    else:
                        st = Student(member_id=mid, student_number=sid, academic_level=academic_level, major=major, affiliation=aff)
                        db.session.add(st)
                    db.session.commit()
                    # Project assignments will be handled below (multi-select)
                elif member_type == 'collaborator':
                    org = request.form.get('organization')
                    contact = request.form.get('contact_info')
                    bio = request.form.get('biography')
                    col = db.session.get(Collaborator, mid)
                    if col:
                        col.organization = org
                        col.contact_info = contact
                        col.biography = bio
                    else:
                        col = Collaborator(member_id=mid, organization=org, contact_info=contact, biography=bio)
                        db.session.add(col)
                    db.session.commit()
                # --- handle WorksOn assignments (optional)
                project_ids = request.form.getlist('project_ids')
                # validate and prepare entries
                work_items = []
                for pid in project_ids:
                    role = (request.form.get(f'role_{pid}') or '').strip()
                    wh = request.form.get(f'weekly_hours_{pid}')
                    try:
                        whf = float(wh)
                    except Exception:
                        flash(f'Weekly hours must be numeric for project {pid}.', 'error')
                        return redirect(url_for('member_edit', mid=mid))
                    if not role:
                        flash(f'Role is required for project {pid}.', 'error')
                        return redirect(url_for('member_edit', mid=mid))
                    work_items.append((pid, role, whf))
                try:
                    # synchronize WorksOn: remove unselected, update existing, add new
                    existing = {wo.project_id: wo for wo in WorksOn.query.filter_by(member_id=mid).all()}
                    selected = set(project_ids)
                    # remove unselected
                    for gid, wo in existing.items():
                        if gid not in selected:
                            try:
                                db.session.delete(wo)
                            except Exception:
                                db.session.rollback()
                    # add/update selected
                    for pid, role, whf in work_items:
                        if pid in existing:
                            ew = existing[pid]
                            ew.role = role
                            ew.weekly_hours = whf
                        else:
                            newwo = WorksOn(member_id=mid, project_id=pid, role=role, weekly_hours=whf)
                            db.session.add(newwo)
                    db.session.commit()
                    flash('Member updated successfully.', 'success')
                    return redirect(url_for('members'))
                except Exception as ex:
                    db.session.rollback()
                    flash(f'Error updating member: {ex}', 'error')
                    return redirect(url_for('member_edit', mid=mid))
            except Exception as ex:
                db.session.rollback()
                flash(f'Error updating member: {ex}', 'error')
                return redirect(url_for('member_edit', mid=mid))
        # pass subtype objects to template to pre-fill fields
        subtype = {}
        if faculty:
            subtype['department'] = faculty.department
            subtype['affiliation'] = faculty.affiliation
            subtype['title'] = faculty.title
            # Faculty biography column removed in schema; do not access
        if student:
            subtype['student_number'] = student.student_number
            subtype['academic_level'] = student.academic_level
            subtype['major'] = student.major
            subtype['affiliation'] = student.affiliation
        if collaborator:
            subtype['organization'] = collaborator.organization
            subtype['contact_info'] = collaborator.contact_info
            subtype['biography'] = collaborator.biography
        projects = Project.query.order_by(Project.project_id).all()
        # prepare existing WorksOn mapping for template
        workson = {wo.project_id: {'role': wo.role, 'weekly_hours': wo.weekly_hours} for wo in WorksOn.query.filter_by(member_id=mid).all()}
        return render_template('member_form.html', member=m, subtype=subtype, projects=projects, workson=workson)

    @app.route('/members/<mid>/delete', methods=['POST'])
    def member_delete(mid):
        m = LabMember.query.get_or_404(mid)
        # prevent deleting a faculty who is a project leader
        leading = Project.query.filter_by(leader_id=mid).count()
        if leading > 0:
            flash('Cannot delete member who is leader of one or more projects. Reassign project leader first.', 'error')
            return redirect(url_for('members'))
        try:
            # delete subtype rows
            Faculty.query.filter_by(member_id=mid).delete()
            Student.query.filter_by(member_id=mid).delete()
            Collaborator.query.filter_by(member_id=mid).delete()
            # delete works-on, equipment use, authorship, mentorship rows referencing this member
            WorksOn.query.filter_by(member_id=mid).delete()
            EquipmentUse.query.filter_by(member_id=mid).delete()
            Authorship.query.filter_by(member_id=mid).delete()
            # mentorship: delete rows where member is mentor or mentee
            Mentorship.query.filter((Mentorship.mentor_id == mid) | (Mentorship.mentee_id == mid)).delete(synchronize_session=False)
            # finally delete base member
            db.session.delete(m)
            db.session.commit()
            flash('Member and dependent records removed.', 'success')
        except Exception as ex:
            db.session.rollback()
            flash(f'Error deleting member and dependents: {ex}', 'error')
        return redirect(url_for('members'))

    # --- Equipment Use CRUD ---
    @app.route('/equipmentuse')
    def equipment_use_list():
        uses = EquipmentUse.query.order_by(EquipmentUse.use_start.desc()).all()
        return render_template('equipmentuse_list.html', uses=uses)

    @app.route('/equipmentuse/new', methods=['GET', 'POST'])
    def equipment_use_new():
        members = LabMember.query.all()
        equipment_list = Equipment.query.all()
        if request.method == 'POST':
            equip_id = request.form.get('equip_id')
            member_id = request.form.get('member_id')
            use_start = _parse_datetime(request.form.get('use_start') or None)
            use_end = _parse_datetime(request.form.get('use_end') or None)
            purpose = request.form.get('purpose')
            # server-side validation: require all fields
            if not (equip_id and member_id and use_start and use_end and purpose):
                flash('All equipment-use fields are required.', 'error')
                return redirect(url_for('equipment_use_new'))
            # check overlapping uses: max 3 concurrent users
            try:
                from sqlalchemy import or_
                cond1 = or_(EquipmentUse.use_end == None, EquipmentUse.use_end >= use_start) if use_start else True
                cond2 = or_(use_end == None, EquipmentUse.use_start <= use_end) if use_end else True
                # build query carefully depending on which dates provided
                q = EquipmentUse.query.filter(EquipmentUse.equip_id == equip_id)
                if use_start:
                    q = q.filter(or_(EquipmentUse.use_end == None, EquipmentUse.use_end >= use_start))
                if use_end:
                    q = q.filter(EquipmentUse.use_start <= use_end)
                overlapping = q.count()
            except Exception:
                overlapping = 0
            if overlapping >= 3:
                flash(f'Cannot schedule use: equipment {equip_id} already in use by {overlapping} members during that time (limit 3).', 'error')
                return redirect(url_for('equipment_use_new'))
            # prevent same member from having overlapping or multiple bookings on same day for same equipment
            try:
                existing = EquipmentUse.query.filter_by(equip_id=equip_id, member_id=member_id).all()
                for ex in existing:
                    if ex.use_start is None:
                        flash('You already have an open booking for this equipment.', 'error')
                        return redirect(url_for('equipment_use_new'))
                    # if both have start/end, check overlap
                    if use_start and use_end and ex.use_start and ex.use_end:
                        if not (ex.use_end < use_start or ex.use_start > use_end):
                            flash('Conflict: you already have an overlapping booking for this equipment.', 'error')
                            return redirect(url_for('equipment_use_new'))
                    # same calendar day conflict (existing booking on same day)
                    try:
                        if use_start and ex.use_start and ex.use_start.date() == use_start.date():
                            flash('Conflict: you already have a booking for this equipment on the same day.', 'error')
                            return redirect(url_for('equipment_use_new'))
                        if use_end and ex.use_end and ex.use_end.date() == use_end.date():
                            flash('Conflict: you already have a booking for this equipment on the same day.', 'error')
                            return redirect(url_for('equipment_use_new'))
                    except Exception:
                        pass
            except Exception:
                pass
            use_id = _get_next_id('U', EquipmentUse, 'use_id')
            eu = EquipmentUse(use_id=use_id, equip_id=equip_id, member_id=member_id, use_start=use_start, use_end=use_end, purpose=purpose)
            try:
                db.session.add(eu)
                db.session.commit()
            except Exception as ex:
                db.session.rollback()
                flash(str(ex), 'error')
                return redirect(url_for('equipment_use_new'))
            return redirect(url_for('equipment'))
        return render_template('equipmentuse_form.html', members=members, equipment_list=equipment_list, use=None)

    @app.route('/equipment/availability')
    def equipment_availability():
        equip_id = request.args.get('equip_id')
        start = request.args.get('start')
        end = request.args.get('end')
        use_start = _parse_datetime(start)
        use_end = _parse_datetime(end)
        try:
            q = EquipmentUse.query.filter(EquipmentUse.equip_id == equip_id)
            if use_start:
                q = q.filter((EquipmentUse.use_end == None) | (EquipmentUse.use_end >= use_start))
            if use_end:
                q = q.filter(EquipmentUse.use_start <= use_end)
            overlapping = q.count()
        except Exception:
            overlapping = 0
        available = overlapping < 3
        return jsonify({'equip_id': equip_id, 'overlapping': overlapping, 'available': available, 'limit': 3})

    @app.route('/equipment/member_conflicts')
    def equipment_member_conflicts():
        equip_id = request.args.get('equip_id')
        member_id = request.args.get('member_id')
        start = request.args.get('start')
        end = request.args.get('end')
        use_start = _parse_datetime(start)
        use_end = _parse_datetime(end)
        conflicts = 0
        try:
            existing = EquipmentUse.query.filter_by(equip_id=equip_id, member_id=member_id).all()
            for ex in existing:
                if ex.use_start is None:
                    conflicts += 1
                    continue
                if use_start and use_end and ex.use_start and ex.use_end:
                    if not (ex.use_end < use_start or ex.use_start > use_end):
                        conflicts += 1
                        continue
                try:
                    if use_start and ex.use_start and ex.use_start.date() == use_start.date():
                        conflicts += 1
                        continue
                    if use_end and ex.use_end and ex.use_end.date() == use_end.date():
                        conflicts += 1
                        continue
                except Exception:
                    pass
        except Exception:
            conflicts = 0
        return jsonify({'conflicts': conflicts, 'allowed': conflicts == 0})

    @app.route('/equipment/users')
    def equipment_users():
        # Return currently active users for a given equipment and their projects
        equip_id = request.args.get('equip_id')
        now = datetime.now()
        users = []
        if not equip_id:
            return jsonify({'equip_id': None, 'users': []})
        try:
            uses = EquipmentUse.query.filter_by(equip_id=equip_id).all()
            for u in uses:
                try:
                    # consider active if no end or end >= now, and start is None or start <= now
                    active = True
                    if u.use_end is not None and u.use_end < now:
                        active = False
                    if u.use_start is not None and u.use_start > now:
                        active = False
                    if not active:
                        continue
                    member = db.session.get(LabMember, u.member_id)
                    if not member:
                        continue
                    # collect projects for member (include role/hours)
                    prows = WorksOn.query.filter_by(member_id=member.member_id).all()
                    projects = []
                    for p in prows:
                        proj = db.session.get(Project, p.project_id)
                        projects.append({'project_id': p.project_id, 'title': proj.title if proj else None, 'role': p.role, 'weekly_hours': p.weekly_hours})
                    users.append({'member_id': member.member_id, 'name': member.name, 'type': member.member_type, 'projects': projects})
                except Exception:
                    continue
        except Exception:
            return jsonify({'equip_id': equip_id, 'users': []}), 200
        return jsonify({'equip_id': equip_id, 'users': users})

    @app.route('/members/search')
    def members_search():
        # Simple member lookup by id and include current equipment uses
        mid = request.args.get('member_id')
        if not mid:
            return jsonify({'error': 'member_id required'}), 400
        m = db.session.get(LabMember, mid)
        if not m:
            return jsonify({'error': 'not found'}), 404
        # current uses
        now = datetime.now()
        current_uses = []
        try:
            uses = EquipmentUse.query.filter_by(member_id=mid).all()
            for u in uses:
                active = True
                if u.use_end is not None and u.use_end < now:
                    active = False
                if u.use_start is not None and u.use_start > now:
                    active = False
                if not active:
                    continue
                equip = db.session.get(Equipment, u.equip_id)
                # try to match this use to one of the member's projects by overlapping dates
                matched_proj_id = None
                matched_proj_name = None
                try:
                    wos = WorksOn.query.filter_by(member_id=mid).all()
                    for wo in wos:
                        proj = db.session.get(Project, wo.project_id)
                        if not proj:
                            continue
                        # if use has start/end, compare with project start/end
                        try:
                            use_s = u.use_start
                            use_e = u.use_end
                            p_s = proj.start_date
                            p_e = proj.end_date
                            overlap = False
                            if use_s and p_s and use_s.date() < p_s:
                                # use starts before project starts -> no overlap by this check
                                pass
                            # general overlap check using available dates
                            if use_s and p_e and use_s.date() <= p_e:
                                overlap = True
                            if use_e and p_s and use_e.date() >= p_s:
                                overlap = True
                            # if project has no dates or use has no dates, accept as potential match
                            if (p_s is None and p_e is None) or (use_s is None and use_e is None):
                                overlap = True
                            if overlap:
                                matched_proj_id = wo.project_id
                                matched_proj_name = proj.title
                                break
                        except Exception:
                            continue
                except Exception:
                    pass
                current_uses.append({'use_id': u.use_id, 'equip_id': u.equip_id, 'equip_name': equip.name if equip else None, 'project_id': matched_proj_id, 'project_name': matched_proj_name})
        except Exception:
            current_uses = []
        # include projects the member currently works on (WorksOn)
        projects = []
        try:
            wos = WorksOn.query.filter_by(member_id=mid).all()
            for wo in wos:
                proj = db.session.get(Project, wo.project_id)
                projects.append({'project_id': wo.project_id, 'title': proj.title if proj else None, 'role': wo.role, 'weekly_hours': wo.weekly_hours})
        except Exception:
            projects = []
        return jsonify({'member_id': m.member_id, 'name': m.name, 'type': m.member_type, 'current_uses': current_uses, 'projects': projects})

    @app.route('/equipmentuse/<uid>/delete', methods=['POST'])
    def equipment_use_delete(uid):
        u = EquipmentUse.query.get_or_404(uid)
        db.session.delete(u)
        db.session.commit()
        return redirect(url_for('equipment'))

    # Example report route: members with highest number of publications
    @app.route('/reports/top_authors')
    def top_authors():
        sql = '''SELECT lm.member_id, lm.name, COUNT(a.pub_id) AS pubs
                 FROM LabMember lm
                 JOIN Authorship a ON lm.member_id = a.member_id
                 GROUP BY lm.member_id, lm.name
                 ORDER BY pubs DESC
                 LIMIT 10;'''
        result = db.session.execute(text(sql)).fetchall()
        return render_template('reports_top_authors.html', rows=result)

    # Average student publications per major
    @app.route('/reports/avg_student_pubs')
    def avg_student_pubs():
        sql = '''SELECT t.major, AVG(t.cnt) as avg_pubs FROM (
                    SELECT st.member_id as member_id, st.major as major, COUNT(a.pub_id) as cnt
                    FROM Student st
                    LEFT JOIN Authorship a ON st.member_id = a.member_id
                    GROUP BY st.member_id, st.major
                 ) as t GROUP BY t.major;'''
        result = db.session.execute(text(sql)).fetchall()
        return render_template('reports_avg_student_pubs.html', rows=result)

    @app.route('/reports/avg_student_pubs.json')
    def avg_student_pubs_json():
        sql = '''SELECT t.major, AVG(t.cnt) as avg_pubs FROM (
                    SELECT st.member_id as member_id, st.major as major, COUNT(a.pub_id) as cnt
                    FROM Student st
                    LEFT JOIN Authorship a ON st.member_id = a.member_id
                    GROUP BY st.member_id, st.major
                 ) as t GROUP BY t.major;'''
        rows = db.session.execute(text(sql)).fetchall()
        data = [{'major': r[0], 'avg_pubs': float(r[1]) if r[1] is not None else 0.0} for r in rows]
        return jsonify({'rows': data})

    # Number of projects funded by a grant and active during a given period (params: start, end)
    @app.route('/reports/projects_active')
    def projects_active():
        start = request.args.get('start') or '2022-01-01'
        end = request.args.get('end') or '2023-12-31'
        sql = '''SELECT COUNT(DISTINCT p.project_id) AS count_projects
                 FROM Project p
                 JOIN ProjectGrant pg ON p.project_id = pg.project_id
                 WHERE NOT (p.end_date < :start OR (p.start_date > :end))
              '''
        result = db.session.execute(text(sql), {'start': start, 'end': end}).fetchall()
        return render_template('reports_projects_active.html', rows=result, start=start, end=end)

    # Three most prolific members who have worked on a project funded by a given grant (grant_id param)
    @app.route('/reports/top3_for_grant')
    def top3_for_grant():
        gid = request.args.get('grant_id') or '1'
        sql = '''SELECT lm.member_id, lm.name, COUNT(DISTINCT a.pub_id) as pubs
                 FROM LabMember lm
                 JOIN WorksOn w ON lm.member_id = w.member_id
                 JOIN ProjectGrant pg ON w.project_id = pg.project_id
                 LEFT JOIN Authorship a ON lm.member_id = a.member_id
                 WHERE pg.grant_id = :gid
                 GROUP BY lm.member_id, lm.name
                 ORDER BY pubs DESC
                 LIMIT 3;'''
        rows = db.session.execute(text(sql), {'gid': gid}).fetchall()
        return render_template('reports_top3_for_grant.html', rows=rows, gid=gid)

    # --- Additional DF navigation and admin views ---
    @app.route('/member-project-manager')
    def member_project_manager():
        return render_template('member_project_manager.html')

    @app.route('/members-manager')
    def members_manager():
        members = LabMember.query.order_by(LabMember.member_id).all()
        return render_template('members_manager.html', members=members)

    @app.route('/projects-manager')
    def projects_manager():
        projects = Project.query.order_by(Project.project_id).all()
        return render_template('projects_manager.html', projects=projects)

    @app.route('/project-status')
    def project_status_page():
        return render_template('project_status.html')

    @app.route('/mentorship-relations')
    def mentorship_relations():
        return render_template('mentorship_relations.html')

    @app.route('/equipment-usage-tracking')
    def equipment_usage_tracking():
        uses = EquipmentUse.query.order_by(EquipmentUse.use_start.desc()).all()
        for u in uses:
            try:
                u.member = db.session.get(LabMember, u.member_id)
            except Exception:
                u.member = None
        return render_template('equipment_usage_tracking.html', uses=uses)

    @app.route('/grant-publication-reporting')
    def grant_publication_reporting():
        return render_template('grant_publication_reporting.html')

    @app.route('/grants/status')
    def grant_status():
        gid = request.args.get('grant_id')
        start_str = request.args.get('start')
        end_str = request.args.get('end')
        start_date = _parse_date(start_str) if start_str else None
        end_date = _parse_date(end_str) if end_str else None
        grant = None
        projects = []
        active_count = None
        if gid:
            # accept numeric id like '1' and prefix with G
            if not gid.startswith('G') and gid.isdigit():
                gid = f'G{gid}'
            grant = db.session.get(GrantFund, gid)
            if grant:
                pgs = ProjectGrant.query.filter_by(grant_id=gid).all()
                for pg in pgs:
                    proj = db.session.get(Project, pg.project_id)
                    # find members working on this project
                    members = []
                    wos = WorksOn.query.filter_by(project_id=pg.project_id).all()
                    for wo in wos:
                        member = db.session.get(LabMember, wo.member_id)
                        members.append({'member': member, 'role': wo.role, 'weekly_hours': wo.weekly_hours})
                    projects.append({'project': proj, 'amount': pg.amount_allocated, 'members': members})
                # compute number of funded projects active in given period
                if start_date or end_date:
                    cnt = 0
                    for pg in pgs:
                        proj = db.session.get(Project, pg.project_id)
                        if not proj:
                            continue
                        # project active if NOT (proj.end_date < start OR proj.start_date > end)
                        active = True
                        try:
                            if start_date and proj.end_date and proj.end_date < start_date:
                                active = False
                            if end_date and proj.start_date and proj.start_date > end_date:
                                active = False
                        except Exception:
                            pass
                        if active:
                            cnt += 1
                    active_count = cnt
        return render_template('grant_status.html', grant=grant, projects=projects, query_gid=gid)

    @app.route('/admin/sql', methods=['GET', 'POST'])
    def sql_editor():
        result = None
        columns = []
        message = None
        sql = ''
        error = None
        if request.method == 'POST':
            sql = request.form.get('sql') or ''
            if not sql.strip():
                error = 'No SQL provided.'
            else:
                try:
                    s = sql.strip()
                    # If SELECT statement (read), fetch rows and display
                    if s.lower().startswith('select'):
                        res = db.session.execute(text(s))
                        rows = res.fetchall()
                        columns = res.keys()
                        result = rows
                    else:
                            # Intercept deletes of LabMember to perform cascading deletes safely
                            m = re.findall(r"delete\s+from\s+labmember\s+where\s+member_id\s*=\s*['\"]?([^'\"\s;]+)['\"]?", s, re.I)
                            if m:
                                # run cascade deletion for each member id found
                                for mid in m:
                                    try:
                                        # prevent deleting if member leads projects
                                        leading = Project.query.filter_by(leader_id=mid).count()
                                        if leading > 0:
                                            raise Exception(f'Cannot delete member {mid}: is leader of {leading} project(s). Reassign leader first.')
                                        Faculty.query.filter_by(member_id=mid).delete()
                                        Student.query.filter_by(member_id=mid).delete()
                                        Collaborator.query.filter_by(member_id=mid).delete()
                                        WorksOn.query.filter_by(member_id=mid).delete()
                                        EquipmentUse.query.filter_by(member_id=mid).delete()
                                        Authorship.query.filter_by(member_id=mid).delete()
                                        Mentorship.query.filter((Mentorship.mentor_id == mid) | (Mentorship.mentee_id == mid)).delete(synchronize_session=False)
                                        lm = db.session.get(LabMember, mid)
                                        if lm:
                                            db.session.delete(lm)
                                        db.session.commit()
                                    except Exception as ex:
                                        db.session.rollback()
                                        error = str(ex)
                                        break
                                if not error:
                                    message = 'Member delete(s) executed with cascading.'
                            else:
                                # For write/ddl statements allow multiple commands via executescript
                                conn = None
                                try:
                                    # use raw connection for executescript to support multiple statements
                                    conn = db.engine.raw_connection()
                                    cur = conn.cursor()
                                    cur.executescript(sql)
                                    conn.commit()
                                    message = 'SQL executed successfully.'
                                finally:
                                    if conn:
                                        conn.close()
                except Exception as ex:
                    # rollback session to stay consistent
                    try:
                        db.session.rollback()
                    except Exception:
                        pass
                    error = str(ex)
        return render_template('sql_editor.html', sql=sql, result=result, columns=columns, message=message, error=error)

    @app.route('/all')
    def all_page():
        return render_template('all_page.html')

    # All Tables View Routes (DF)
    @app.route('/view/members')
    def view_all_members():
        members = LabMember.query.order_by(LabMember.member_id).all()
        return render_template('members.html', members=members)

    @app.route('/view/faculty')
    def view_faculty():
        faculty = Faculty.query.order_by(Faculty.member_id).all()
        return render_template('view_faculty.html', faculty=faculty)

    @app.route('/view/students')
    def view_students():
        students = Student.query.order_by(Student.member_id).all()
        return render_template('view_students.html', students=students)

    @app.route('/view/collaborators')
    def view_collaborators():
        collaborators = Collaborator.query.order_by(Collaborator.member_id).all()
        return render_template('view_collaborators.html', collaborators=collaborators)

    @app.route('/view/projects')
    def view_all_projects():
        projects = Project.query.order_by(Project.project_id).all()
        return render_template('projects.html', projects=projects)

    @app.route('/view/works-on')
    def view_works_on():
        works_on = WorksOn.query.order_by(WorksOn.member_id).all()
        for w in works_on:
            try:
                w.member = db.session.get(LabMember, w.member_id)
            except Exception:
                w.member = None
        return render_template('view_works_on.html', works_on=works_on)

    # WorksOn CRUD
    @app.route('/workson/new', methods=['GET', 'POST'])
    def workson_new():
        members = LabMember.query.order_by(LabMember.member_id).all()
        projects = Project.query.order_by(Project.project_id).all()
        if request.method == 'POST':
            member_id = request.form.get('member_id')
            project_id = request.form.get('project_id')
            role = request.form.get('role')
            weekly_hours = request.form.get('weekly_hours')
            existing = WorksOn.query.filter_by(member_id=member_id, project_id=project_id).first()
            if existing:
                flash('This member is already assigned to this project.', 'error')
                return redirect(url_for('workson_new'))
            wo = WorksOn(member_id=member_id, project_id=project_id, role=role, weekly_hours=weekly_hours)
            db.session.add(wo)
            db.session.commit()
            flash(f'Member {member_id} assigned to project {project_id}.', 'success')
            return redirect(url_for('view_works_on'))
        return render_template('workson_form.html', members=members, projects=projects, workson=None)

    @app.route('/workson/<string:member_id>/<string:project_id>/edit', methods=['GET', 'POST'])
    def workson_edit(member_id, project_id):
        wo = WorksOn.query.filter_by(member_id=member_id, project_id=project_id).first_or_404()
        members = LabMember.query.order_by(LabMember.member_id).all()
        projects = Project.query.order_by(Project.project_id).all()
        if request.method == 'POST':
            wo.role = request.form.get('role')
            wo.weekly_hours = request.form.get('weekly_hours')
            db.session.commit()
            flash('Assignment updated.', 'success')
            return redirect(url_for('view_works_on'))
        return render_template('workson_form.html', members=members, projects=projects, workson=wo)

    @app.route('/workson/<string:member_id>/<string:project_id>/delete', methods=['POST'])
    def workson_delete(member_id, project_id):
        wo = WorksOn.query.filter_by(member_id=member_id, project_id=project_id).first_or_404()
        db.session.delete(wo)
        db.session.commit()
        flash('Assignment removed.', 'success')
        return redirect(url_for('view_works_on'))

    @app.route('/view/grants')
    def view_all_grants():
        grants = GrantFund.query.order_by(GrantFund.grant_id).all()
        return render_template('grants.html', grants=grants)

    @app.route('/projectgrant/new', methods=['GET', 'POST'])
    def projectgrant_new():
        projects = Project.query.order_by(Project.project_id).all()
        grants = GrantFund.query.order_by(GrantFund.grant_id).all()
        if request.method == 'POST':
            project_id = request.form.get('project_id')
            grant_id = request.form.get('grant_id')
            amount_allocated = request.form.get('amount_allocated')
            existing = ProjectGrant.query.filter_by(project_id=project_id, grant_id=grant_id).first()
            if existing:
                flash('This grant is already allocated to this project.', 'error')
                return redirect(url_for('projectgrant_new'))
            pg = ProjectGrant(project_id=project_id, grant_id=grant_id, amount_allocated=amount_allocated)
            db.session.add(pg)
            db.session.commit()
            flash(f'Grant {grant_id} allocated to project {project_id}.', 'success')
            return redirect(url_for('view_project_grant'))
        return render_template('projectgrant_form.html', projects=projects, grants=grants, projectgrant=None)

    @app.route('/projectgrant/<string:project_id>/<string:grant_id>/edit', methods=['GET', 'POST'])
    def projectgrant_edit(project_id, grant_id):
        pg = ProjectGrant.query.filter_by(project_id=project_id, grant_id=grant_id).first_or_404()
        projects = Project.query.order_by(Project.project_id).all()
        grants = GrantFund.query.order_by(GrantFund.grant_id).all()
        if request.method == 'POST':
            pg.amount_allocated = request.form.get('amount_allocated')
            db.session.commit()
            flash('Grant allocation updated.', 'success')
            return redirect(url_for('view_project_grant'))
        return render_template('projectgrant_form.html', projects=projects, grants=grants, projectgrant=pg)

    @app.route('/projectgrant/<string:project_id>/<string:grant_id>/delete', methods=['POST'])
    def projectgrant_delete(project_id, grant_id):
        pg = ProjectGrant.query.filter_by(project_id=project_id, grant_id=grant_id).first_or_404()
        db.session.delete(pg)
        db.session.commit()
        flash('Grant allocation removed.', 'success')
        return redirect(url_for('view_project_grant'))

    # /view/project-grant removed (project grant viewing is available via grants/project pages)

    @app.route('/view/project-grant')
    def view_project_grant_redirect():
        # Redirect legacy All-page link to canonical grants page
        return redirect(url_for('grants'))

    @app.route('/view/equipment')
    def view_all_equipment():
        equipment = Equipment.query.order_by(Equipment.equip_id).all()
        return render_template('equipment.html', equipment=equipment)

    # /view/equipment-use removed (equipment usage tracked via equipment pages)

    @app.route('/view/equipment-use')
    def view_equipment_use_redirect():
        # Redirect legacy All-page link to equipment usage tracking
        return redirect(url_for('equipment_usage_tracking'))

    @app.route('/view/publications')
    def view_all_publications():
        pubs = Publication.query.order_by(Publication.pub_id).all()
        return render_template('publications.html', pubs=pubs)

    @app.route('/view/authorship')
    def view_authorship():
        authorship = Authorship.query.order_by(Authorship.pub_id).all()
        for a in authorship:
            try:
                a.member = db.session.get(LabMember, a.member_id)
            except Exception:
                a.member = None
            try:
                a.publication = db.session.get(Publication, a.pub_id)
            except Exception:
                a.publication = None
        return render_template('view_authorship.html', authorship=authorship)

    @app.route('/authorship/new', methods=['GET', 'POST'])
    def authorship_new():
        pubs = Publication.query.order_by(Publication.pub_id).all()
        members = LabMember.query.order_by(LabMember.member_id).all()
        if request.method == 'POST':
            pub_id = request.form.get('pub_id')
            member_id = request.form.get('member_id')
            author_order = request.form.get('author_order')
            author_role = request.form.get('author_role')
            if not (pub_id and member_id):
                flash('Publication and member are required.', 'error')
                return redirect(url_for('authorship_new'))
            existing = Authorship.query.filter_by(pub_id=pub_id, member_id=member_id).first()
            if existing:
                flash('This authorship already exists.', 'error')
                return redirect(url_for('authorship_new'))
            try:
                ao = int(author_order) if author_order else None
            except Exception:
                flash('Author order must be an integer.', 'error')
                return redirect(url_for('authorship_new'))
            a = Authorship(pub_id=pub_id, member_id=member_id, author_order=ao, author_role=author_role)
            try:
                db.session.add(a)
                db.session.commit()
                flash('Author added to publication.', 'success')
                return redirect(url_for('view_authorship'))
            except Exception as ex:
                db.session.rollback()
                flash(f'Error adding authorship: {ex}', 'error')
                return redirect(url_for('authorship_new'))
        return render_template('authorship_form.html', pubs=pubs, members=members, authorship=None)

    @app.route('/authorship/<string:pub_id>/<string:member_id>/edit', methods=['GET', 'POST'])
    def authorship_edit(pub_id, member_id):
        a = Authorship.query.filter_by(pub_id=pub_id, member_id=member_id).first_or_404()
        pubs = Publication.query.order_by(Publication.pub_id).all()
        members = LabMember.query.order_by(LabMember.member_id).all()
        if request.method == 'POST':
            try:
                a.author_order = int(request.form.get('author_order')) if request.form.get('author_order') else None
            except Exception:
                flash('Author order must be an integer.', 'error')
                return redirect(url_for('authorship_edit', pub_id=pub_id, member_id=member_id))
            a.author_role = request.form.get('author_role')
            try:
                db.session.commit()
                flash('Authorship updated.', 'success')
                return redirect(url_for('view_authorship'))
            except Exception as ex:
                db.session.rollback()
                flash(f'Error updating authorship: {ex}', 'error')
                return redirect(url_for('authorship_edit', pub_id=pub_id, member_id=member_id))
        return render_template('authorship_form.html', pubs=pubs, members=members, authorship=a)

    @app.route('/authorship/<string:pub_id>/<string:member_id>/delete', methods=['POST'])
    def authorship_delete(pub_id, member_id):
        a = Authorship.query.filter_by(pub_id=pub_id, member_id=member_id).first_or_404()
        try:
            db.session.delete(a)
            db.session.commit()
            flash('Authorship removed.', 'success')
        except Exception as ex:
            db.session.rollback()
            flash(f'Error removing authorship: {ex}', 'error')
        return redirect(url_for('view_authorship'))

    @app.route('/view/mentorship')
    def view_mentorship():
        mentorships = Mentorship.query.order_by(Mentorship.mentor_id).all()
        for m in mentorships:
            try:
                m.mentor = db.session.get(LabMember, m.mentor_id)
            except Exception:
                m.mentor = None
            try:
                m.mentee = db.session.get(LabMember, m.mentee_id)
            except Exception:
                m.mentee = None
        return render_template('view_mentorship.html', mentorships=mentorships)

    @app.route('/mentorship/new', methods=['GET', 'POST'])
    def mentorship_new():
        members = LabMember.query.order_by(LabMember.member_id).all()
        if request.method == 'POST':
            mentor_id = request.form.get('mentor_id')
            mentee_id = request.form.get('mentee_id')
            start_date = _parse_date(request.form.get('start_date'))
            if not start_date:
                flash('Start date is required for mentorship.', 'error')
                return redirect(url_for('mentorship_new'))
            end_date = _parse_date(request.form.get('end_date'))
            notes = request.form.get('notes')
            if mentor_id == mentee_id:
                flash('Mentor and mentee cannot be the same person.', 'error')
                return redirect(url_for('mentorship_new'))
            existing = Mentorship.query.filter_by(mentee_id=mentee_id).all()
            for ex in existing:
                ex_end = ex.end_date
                ex_start = ex.start_date
                if not (ex_end is not None and ex_end < start_date) and not (end_date is not None and end_date < ex_start):
                    flash(f'Mentee {mentee_id} already has a mentorship overlapping this time frame.', 'error')
                    return redirect(url_for('mentorship_new'))
            m = Mentorship(mentor_id=mentor_id, mentee_id=mentee_id, start_date=start_date, end_date=end_date, notes=notes)
            try:
                db.session.add(m)
                db.session.commit()
            except IntegrityError as ie:
                db.session.rollback()
                raw = str(ie.orig) if hasattr(ie, 'orig') else str(ie)
                if 'Students cannot mentor faculty' in raw:
                    flash(f'Students cannot mentor faculty: {mentor_id} → {mentee_id}', 'error')
                else:
                    flash(raw, 'error')
                return redirect(url_for('mentorship_new'))
            flash(f'Mentorship created: {mentor_id} → {mentee_id}.', 'success')
            return redirect(url_for('view_mentorship'))
        return render_template('mentorship_form.html', members=members, mentorship=None)

    # Mentorship CRUD - Edit
    @app.route('/mentorship/<string:mentor_id>/<string:mentee_id>/edit', methods=['GET', 'POST'])
    def mentorship_edit(mentor_id, mentee_id):
        m = Mentorship.query.filter_by(mentor_id=mentor_id, mentee_id=mentee_id).first_or_404()
        members = LabMember.query.order_by(LabMember.member_id).all()
        if request.method == 'POST':
            m.start_date = _parse_date(request.form.get('start_date'))
            # enforce start_date presence on edit
            if not m.start_date:
                flash('Start date is required for mentorship.', 'error')
                return redirect(url_for('mentorship_edit', mentor_id=mentor_id, mentee_id=mentee_id))
            m.end_date = _parse_date(request.form.get('end_date'))
            m.notes = request.form.get('notes')
            # safety: prevent self-mentorship
            if m.mentor_id == m.mentee_id:
                flash('Mentor and mentee cannot be the same person.', 'error')
                return redirect(url_for('mentorship_edit', mentor_id=mentor_id, mentee_id=mentee_id))

            # server-side: ensure mentee doesn't have overlapping mentorships (exclude current record)
            existing = Mentorship.query.filter(Mentorship.mentee_id == m.mentee_id).all()
            for ex in existing:
                if ex.mentor_id == mentor_id and ex.mentee_id == mentee_id:
                    continue
                ex_end = ex.end_date
                ex_start = ex.start_date
                if not (ex_end is not None and ex_end < m.start_date) and not (m.end_date is not None and m.end_date < ex_start):
                    flash(f'Mentee {m.mentee_id} already has a mentorship overlapping this time frame.', 'error')
                    return redirect(url_for('mentorship_edit', mentor_id=mentor_id, mentee_id=mentee_id))
            try:
                db.session.commit()
            except IntegrityError as ie:
                db.session.rollback()
                raw = str(ie.orig) if hasattr(ie, 'orig') else str(ie)
                if 'Students cannot mentor faculty' in raw:
                    flash(f'Students cannot mentor faculty: {m.mentor_id} → {m.mentee_id}', 'error')
                else:
                    flash(raw, 'error')
                return redirect(url_for('mentorship_edit', mentor_id=mentor_id, mentee_id=mentee_id))
            flash('Mentorship updated.', 'success')
            return redirect(url_for('view_mentorship'))
        return render_template('mentorship_form.html', members=members, mentorship=m)

    # Mentorship CRUD - Delete
    @app.route('/mentorship/<string:mentor_id>/<string:mentee_id>/delete', methods=['POST'])
    def mentorship_delete(mentor_id, mentee_id):
        m = Mentorship.query.filter_by(mentor_id=mentor_id, mentee_id=mentee_id).first_or_404()
        db.session.delete(m)
        db.session.commit()
        flash('Mentorship removed.', 'success')
        return redirect(url_for('view_mentorship'))

    
    @app.teardown_request
    def shutdown_session(exception=None):
        # ensure any pending changes are committed when request finishes successfully
        try:
            if exception is None:
                db.session.commit()
        except Exception:
            try:
                db.session.rollback()
            except Exception:
                pass
        finally:
            db.session.remove()
    @app.after_request
    def commit_after_request(response):
        # commit after any successful write HTTP methods to ensure persistence
        try:
            if request.method in ('POST', 'PUT', 'DELETE') and response.status_code < 400:
                db.session.commit()
        except Exception:
            try:
                db.session.rollback()
            except Exception:
                pass
        return response

    @app.teardown_appcontext
    def remove_session(exception=None):
        # always remove session at appcontext teardown
        try:
            db.session.remove()
        except Exception:
            pass

    @app.errorhandler(Exception)
    def handle_exception(e):
        # on unhandled exceptions, rollback to avoid leaving pending state
        try:
            db.session.rollback()
        except Exception:
            pass
        raise

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
