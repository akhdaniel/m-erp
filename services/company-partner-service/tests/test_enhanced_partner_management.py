"""
Tests for Enhanced Partner Management functionality.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.partner import Partner
from app.models.partner_category import PartnerCategory
from app.models.partner_communication import PartnerCommunication
from app.models.company import Company
from app.services.partner_category_service import PartnerCategoryService
from app.services.partner_communication_service import PartnerCommunicationService
from app.schemas.partner_category import PartnerCategoryCreate, PartnerCategoryUpdate
from app.schemas.partner_communication import PartnerCommunicationCreate, PartnerCommunicationUpdate


class TestPartnerCategory:
    """Test partner category functionality."""
    
    def test_create_partner_category(self, db: Session, test_company: Company):
        """Test creating a partner category."""
        category_service = PartnerCategoryService()
        
        category_data = PartnerCategoryCreate(
            company_id=test_company.id,
            name="Test Customers",
            code="TEST_CUSTOMERS",
            description="Test customer category",
            color="#4CAF50",
            is_active=True
        )
        
        category = category_service.create(db, category_data)
        
        assert category.id is not None
        assert category.name == "Test Customers"
        assert category.code == "TEST_CUSTOMERS"
        assert category.company_id == test_company.id
        assert category.color == "#4CAF50"
        assert category.is_active is True
    
    def test_category_hierarchy(self, db: Session, test_company: Company):
        """Test hierarchical category relationships."""
        category_service = PartnerCategoryService()
        
        # Create parent category
        parent_data = PartnerCategoryCreate(
            company_id=test_company.id,
            name="Customers",
            code="CUSTOMERS",
            description="All customers"
        )
        parent = category_service.create(db, parent_data)
        
        # Create child category
        child_data = PartnerCategoryCreate(
            company_id=test_company.id,
            name="VIP Customers",
            code="VIP_CUSTOMERS",
            description="VIP customer category",
            parent_category_id=parent.id
        )
        child = category_service.create(db, child_data)
        
        # Verify relationships
        db.refresh(parent)
        db.refresh(child)
        
        assert child.parent_category_id == parent.id
        assert child.has_parent is True
        assert parent.is_parent is True
        assert len(parent.child_categories) == 1
        assert parent.child_categories[0].id == child.id
    
    def test_category_tree(self, db: Session, test_company: Company):
        """Test category tree generation."""
        category_service = PartnerCategoryService()
        
        # Create categories with hierarchy
        root1_data = PartnerCategoryCreate(
            company_id=test_company.id,
            name="Customers",
            code="CUSTOMERS"
        )
        root1 = category_service.create(db, root1_data)
        
        child1_data = PartnerCategoryCreate(
            company_id=test_company.id,
            name="VIP Customers",
            code="VIP_CUSTOMERS",
            parent_category_id=root1.id
        )
        child1 = category_service.create(db, child1_data)
        
        root2_data = PartnerCategoryCreate(
            company_id=test_company.id,
            name="Suppliers",
            code="SUPPLIERS"
        )
        root2 = category_service.create(db, root2_data)
        
        # Get category tree
        tree = category_service.get_category_tree(db, test_company.id)
        
        assert len(tree) == 2  # Two root categories
        
        # Find customers category in tree
        customers_node = next(node for node in tree if node.code == "CUSTOMERS")
        assert len(customers_node.children) == 1
        assert customers_node.children[0].code == "VIP_CUSTOMERS"
        
        # Find suppliers category
        suppliers_node = next(node for node in tree if node.code == "SUPPLIERS")
        assert len(suppliers_node.children) == 0
    
    def test_create_default_categories(self, db: Session, test_company: Company):
        """Test creating default categories for a company."""
        category_service = PartnerCategoryService()
        
        categories = category_service.create_default_categories(db, test_company.id)
        
        assert len(categories) >= 3  # At least customers, suppliers, vendors
        
        codes = [cat.code for cat in categories]
        assert "CUSTOMERS" in codes
        assert "SUPPLIERS" in codes
        assert "VENDORS" in codes
        
        # Verify they're saved in database
        db_categories = db.query(PartnerCategory).filter(
            PartnerCategory.company_id == test_company.id
        ).all()
        assert len(db_categories) >= 3
    
    def test_validate_hierarchy_circular_reference(self, db: Session, test_company: Company):
        """Test validation prevents circular references."""
        category_service = PartnerCategoryService()
        
        # Create parent and child
        parent_data = PartnerCategoryCreate(
            company_id=test_company.id,
            name="Parent",
            code="PARENT"
        )
        parent = category_service.create(db, parent_data)
        
        child_data = PartnerCategoryCreate(
            company_id=test_company.id,
            name="Child",
            code="CHILD",
            parent_category_id=parent.id
        )
        child = category_service.create(db, child_data)
        
        # Try to make parent a child of child (circular reference)
        is_valid = category_service.validate_hierarchy(db, parent.id, child.id)
        assert is_valid is False
        
        # Valid hierarchy should work
        grandchild_data = PartnerCategoryCreate(
            company_id=test_company.id,
            name="Grandchild",
            code="GRANDCHILD"
        )
        grandchild = category_service.create(db, grandchild_data)
        
        is_valid = category_service.validate_hierarchy(db, grandchild.id, child.id)
        assert is_valid is True


class TestPartnerCommunication:
    """Test partner communication functionality."""
    
    def test_create_communication(self, db: Session, test_partner: Partner):
        """Test creating a communication record."""
        communication_service = PartnerCommunicationService()
        
        communication_data = PartnerCommunicationCreate(
            partner_id=test_partner.id,
            communication_type="email",
            subject="Test Communication",
            content="This is a test communication",
            direction="outbound",
            status="pending",
            priority="normal"
        )
        
        communication = communication_service.create(db, communication_data)
        
        assert communication.id is not None
        assert communication.partner_id == test_partner.id
        assert communication.subject == "Test Communication"
        assert communication.communication_type == "email"
        assert communication.direction == "outbound"
        assert communication.status == "pending"
        assert communication.priority == "normal"
    
    def test_mark_communication_completed(self, db: Session, test_partner: Partner):
        """Test marking communication as completed."""
        communication_service = PartnerCommunicationService()
        
        # Create communication
        communication_data = PartnerCommunicationCreate(
            partner_id=test_partner.id,
            communication_type="phone",
            subject="Test Call",
            status="pending",
            scheduled_at=datetime.utcnow()
        )
        communication = communication_service.create(db, communication_data)
        
        # Mark as completed
        updated_comm = communication_service.mark_completed(
            db, communication.id, "Successful call"
        )
        
        assert updated_comm.status == "completed"
        assert updated_comm.outcome == "Successful call"
        assert updated_comm.completed_at is not None
        assert updated_comm.is_completed is True
    
    def test_schedule_follow_up(self, db: Session, test_partner: Partner):
        """Test scheduling follow-up."""
        communication_service = PartnerCommunicationService()
        
        # Create communication
        communication_data = PartnerCommunicationCreate(
            partner_id=test_partner.id,
            communication_type="meeting",
            subject="Initial Meeting"
        )
        communication = communication_service.create(db, communication_data)
        
        # Schedule follow-up
        follow_up_date = datetime.utcnow() + timedelta(days=7)
        updated_comm = communication_service.schedule_follow_up(
            db, communication.id, follow_up_date, required=True
        )
        
        assert updated_comm.follow_up_required is True
        assert updated_comm.follow_up_date == follow_up_date
        assert updated_comm.needs_follow_up is True
    
    def test_get_pending_communications(self, db: Session, test_partner: Partner):
        """Test getting pending communications."""
        communication_service = PartnerCommunicationService()
        
        # Create pending communication scheduled for tomorrow
        tomorrow = datetime.utcnow() + timedelta(days=1)
        communication_data = PartnerCommunicationCreate(
            partner_id=test_partner.id,
            communication_type="email",
            subject="Pending Email",
            status="pending",
            scheduled_at=tomorrow
        )
        communication_service.create(db, communication_data)
        
        # Create completed communication (should not appear)
        completed_data = PartnerCommunicationCreate(
            partner_id=test_partner.id,
            communication_type="phone",
            subject="Completed Call",
            status="completed"
        )
        communication_service.create(db, completed_data)
        
        # Get pending communications
        pending = communication_service.get_pending_communications(
            db, test_partner.id, days_ahead=7
        )
        
        assert len(pending) == 1
        assert pending[0].subject == "Pending Email"
        assert pending[0].status == "pending"
    
    def test_get_overdue_communications(self, db: Session, test_partner: Partner):
        """Test getting overdue communications."""
        communication_service = PartnerCommunicationService()
        
        # Create overdue communication
        yesterday = datetime.utcnow() - timedelta(days=1)
        overdue_data = PartnerCommunicationCreate(
            partner_id=test_partner.id,
            communication_type="meeting",
            subject="Overdue Meeting",
            status="pending",
            scheduled_at=yesterday
        )
        communication_service.create(db, overdue_data)
        
        # Create future communication (should not appear)
        tomorrow = datetime.utcnow() + timedelta(days=1)
        future_data = PartnerCommunicationCreate(
            partner_id=test_partner.id,
            communication_type="email",
            subject="Future Email",
            status="pending",
            scheduled_at=tomorrow
        )
        communication_service.create(db, future_data)
        
        # Get overdue communications
        overdue = communication_service.get_overdue_communications(db, test_partner.id)
        
        assert len(overdue) == 1
        assert overdue[0].subject == "Overdue Meeting"
        assert overdue[0].is_overdue is True
    
    def test_communication_statistics(self, db: Session, test_partner: Partner):
        """Test communication statistics generation."""
        communication_service = PartnerCommunicationService()
        
        # Create various communications
        communications_data = [
            {
                "communication_type": "email",
                "subject": "Email 1",
                "status": "completed",
                "priority": "normal"
            },
            {
                "communication_type": "email", 
                "subject": "Email 2",
                "status": "pending",
                "priority": "high"
            },
            {
                "communication_type": "phone",
                "subject": "Call 1",
                "status": "completed",
                "priority": "normal"
            }
        ]
        
        for data in communications_data:
            comm_data = PartnerCommunicationCreate(
                partner_id=test_partner.id,
                **data
            )
            communication_service.create(db, comm_data)
        
        # Get statistics
        stats = communication_service.get_statistics(db, test_partner.id)
        
        assert stats.total_communications == 3
        assert stats.completed_communications == 2
        assert stats.pending_communications == 1
        assert stats.communications_by_type["email"] == 2
        assert stats.communications_by_type["phone"] == 1
        assert stats.communications_by_priority["normal"] == 2
        assert stats.communications_by_priority["high"] == 1


class TestPartnerCategoryIntegration:
    """Test integration between partners and categories."""
    
    def test_partner_with_category(self, db: Session, test_company: Company):
        """Test assigning category to partner."""
        category_service = PartnerCategoryService()
        
        # Create category
        category_data = PartnerCategoryCreate(
            company_id=test_company.id,
            name="VIP Customers",
            code="VIP_CUSTOMERS"
        )
        category = category_service.create(db, category_data)
        
        # Create partner with category
        partner = Partner(
            company_id=test_company.id,
            name="VIP Customer",
            code="VIP001",
            category_id=category.id,
            is_customer=True
        )
        db.add(partner)
        db.commit()
        db.refresh(partner)
        
        # Verify relationship
        assert partner.category_id == category.id
        assert partner.category.name == "VIP Customers"
        
        # Verify category has partner
        db.refresh(category)
        assert category.get_partner_count() == 1
    
    def test_move_partners_between_categories(self, db: Session, test_company: Company):
        """Test moving partners between categories."""
        category_service = PartnerCategoryService()
        
        # Create categories
        old_category_data = PartnerCategoryCreate(
            company_id=test_company.id,
            name="Old Category",
            code="OLD_CAT"
        )
        old_category = category_service.create(db, old_category_data)
        
        new_category_data = PartnerCategoryCreate(
            company_id=test_company.id,
            name="New Category", 
            code="NEW_CAT"
        )
        new_category = category_service.create(db, new_category_data)
        
        # Create partners in old category
        partners = []
        for i in range(3):
            partner = Partner(
                company_id=test_company.id,
                name=f"Partner {i+1}",
                code=f"P{i+1:03d}",
                category_id=old_category.id
            )
            db.add(partner)
            partners.append(partner)
        
        db.commit()
        
        # Move partners to new category
        moved_count = category_service.move_partners_to_category(
            db, old_category.id, new_category.id, test_company.id
        )
        
        assert moved_count == 3
        
        # Verify partners were moved
        for partner in partners:
            db.refresh(partner)
            assert partner.category_id == new_category.id
        
        # Verify category counts
        db.refresh(old_category)
        db.refresh(new_category)
        assert old_category.get_partner_count() == 0
        assert new_category.get_partner_count() == 3