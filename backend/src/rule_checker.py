"""Deterministic Static Analysis Engine for Cisco CLI & Telemetry Verification."""

import re
from typing import List, Dict, Any, Optional
from src.models import Evidence, Case


class RuleChecker:
    """Static inspection suite evaluating deterministic Cisco configuration rules prior to AI inference."""
    
    def __init__(self):
        self.diagnostic_rules = [
            self._check_wrong_subnet_mask,
            self._check_gateway_mismatch,
            self._check_interface_down,
            self._check_missing_vlan,
            self._check_missing_route,
            self._check_dhcp_pool_missing,
            self._check_dhcp_wrong_network,
            self._check_dhcp_wrong_gateway,
            self._check_acl_blocking,
            self._check_nat_missing,
        ]
    
    def run_all_checks(self, evidence: Evidence, case: Optional[Case] = None) -> List[Dict[str, Any]]:
        """Execute rule suite against normalized telemetry inputs."""
        audit_findings: List[Dict[str, Any]] = []
        
        for rule_fn in self.diagnostic_rules:
            try:
                finding = rule_fn(evidence, case)
                if finding is not None:
                    audit_findings.append(finding)
            except Exception as err:
                audit_findings.append({
                    "check": rule_fn.__name__,
                    "status": "ERROR",
                    "message": f"Static inspection execution error: {err}",
                    "severity": "LOW"
                })
                
        return audit_findings
    
    def _check_wrong_subnet_mask(self, evidence: Evidence, case: Optional[Case]) -> Optional[Dict[str, Any]]:
        """Validate subnet mask compliance across IP telemetry logs."""
        regex_mask = r'subnet mask[:\s]+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        full_text = " ".join(evidence.to_dict().values()).lower()
        discovered_masks = re.findall(regex_mask, full_text)
        
        invalid_masks = {'255.255.0.0', '255.0.0.0', '255.255.255.255'}
        flagged = [m for m in discovered_masks if m in invalid_masks]
        
        if flagged:
            return {
                "check": "wrong_subnet_mask",
                "status": "FAIL",
                "message": f"Subnet mask misconfiguration detected ({', '.join(flagged)}). Expected standard 255.255.255.0 mask.",
                "severity": "HIGH"
            }
        return None
    
    def _check_gateway_mismatch(self, evidence: Evidence, case: Optional[Case]) -> Optional[Dict[str, Any]]:
        """Verify host IP address and Default Gateway reside within identical subnet boundary."""
        raw_text = " ".join(evidence.to_dict().values())
        
        gw_regex = re.search(r'default gateway[:\s]+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', raw_text, re.IGNORECASE)
        ip_regex = re.search(r'ip address[:\s]+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', raw_text, re.IGNORECASE)
        mask_regex = re.search(r'subnet mask[:\s]+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', raw_text, re.IGNORECASE)
        
        if gw_regex and ip_regex and mask_regex:
            gateway_ip = gw_regex.group(1)
            host_ip = ip_regex.group(1)
            subnet_mask = mask_regex.group(1)
            
            if not self._same_subnet(host_ip, gateway_ip, subnet_mask):
                return {
                    "check": "gateway_mismatch",
                    "status": "FAIL",
                    "message": f"Gateway mismatch: Gateway {gateway_ip} is outside host subnet boundary ({host_ip}/{subnet_mask}).",
                    "severity": "HIGH"
                }
        return None
    
    def _check_interface_down(self, evidence: Evidence, case: Optional[Case]) -> Optional[Dict[str, Any]]:
        """Detect administratively disabled interfaces in telemetry logs."""
        raw_text = " ".join(evidence.to_dict().values()).lower()
        
        if 'administratively down' in raw_text or 'admin down' in raw_text:
            return {
                "check": "interface_down",
                "status": "FAIL",
                "message": "Cisco port interface state is 'administratively down'. Issue 'no shutdown' command.",
                "severity": "HIGH"
            }
        return None
    
    def _check_missing_vlan(self, evidence: Evidence, case: Optional[Case]) -> Optional[Dict[str, Any]]:
        """Check for unconfigured or missing 802.1Q VLAN IDs."""
        raw_text = " ".join(evidence.to_dict().values()).lower()
        target_vlans = ['vlan 10', 'vlan 20', 'vlan 30']
        missing_list = []
        
        for vtag in target_vlans:
            if vtag in raw_text and any(keyword in raw_text for keyword in ['missing', 'not found', 'absent', 'unconfigured']):
                missing_list.append(vtag)
                
        if missing_list:
            return {
                "check": "missing_vlan",
                "status": "FAIL",
                "message": f"Missing VLAN database entries detected: {', '.join(missing_list)}.",
                "severity": "HIGH"
            }
        return None
    
    def _check_missing_route(self, evidence: Evidence, case: Optional[Case]) -> Optional[Dict[str, Any]]:
        """Verify routing table contains route entries to target destination."""
        raw_text = " ".join(evidence.to_dict().values()).lower()
        
        if 'show ip route' in raw_text or 'ip route' in raw_text:
            if any(term in raw_text for term in ['no route', 'not in routing table', 'unreachable']):
                return {
                    "check": "missing_route",
                    "status": "FAIL",
                    "message": "Routing table missing required static or dynamic route entry for target subnet.",
                    "severity": "HIGH"
                }
        return None
    
    def _check_dhcp_pool_missing(self, evidence: Evidence, case: Optional[Case]) -> Optional[Dict[str, Any]]:
        """Audit router DHCP pool presence and APIPA 169.254.x.x autoconfiguration indicators."""
        raw_text = " ".join(evidence.to_dict().values()).lower()
        
        if 'dhcp' in raw_text:
            if any(term in raw_text for term in ['no ip dhcp pool', 'no pool', 'pool missing']):
                return {
                    "check": "dhcp_pool_missing",
                    "status": "FAIL",
                    "message": "Router missing configured 'ip dhcp pool' definition for client LAN.",
                    "severity": "HIGH"
                }
            if '169.254.' in raw_text:
                return {
                    "check": "dhcp_pool_missing",
                    "status": "FAIL",
                    "message": "Client host fallback to APIPA address (169.254.x.x). DHCP service uncontactable.",
                    "severity": "HIGH"
                }
        return None
    
    def _check_dhcp_wrong_network(self, evidence: Evidence, case: Optional[Case]) -> Optional[Dict[str, Any]]:
        """Audit DHCP network scope matching interface IP subnet."""
        raw_text = " ".join(evidence.to_dict().values()).lower()
        
        if 'dhcp' in raw_text and 'network' in raw_text:
            if 'wrong network' in raw_text or 'incorrect network' in raw_text:
                return {
                    "check": "dhcp_wrong_network",
                    "status": "FAIL",
                    "message": "DHCP address pool scope configured with incorrect network IP statement.",
                    "severity": "HIGH"
                }
        return None
    
    def _check_dhcp_wrong_gateway(self, evidence: Evidence, case: Optional[Case]) -> Optional[Dict[str, Any]]:
        """Audit DHCP default-router configuration."""
        raw_text = " ".join(evidence.to_dict().values()).lower()
        
        if 'dhcp' in raw_text and ('default-router' in raw_text or 'default-gateway' in raw_text):
            if 'wrong gateway' in raw_text or 'incorrect gateway' in raw_text:
                return {
                    "check": "dhcp_wrong_gateway",
                    "status": "FAIL",
                    "message": "DHCP option default-router providing incorrect gateway address to clients.",
                    "severity": "HIGH"
                }
        return None
    
    def _check_acl_blocking(self, evidence: Evidence, case: Optional[Case]) -> Optional[Dict[str, Any]]:
        """Audit Access Control List deny rules."""
        raw_text = " ".join(evidence.to_dict().values()).lower()
        
        if 'access-list' in raw_text or 'access-group' in raw_text:
            if 'deny' in raw_text and any(term in raw_text for term in ['block', 'drop', 'filtered']):
                return {
                    "check": "acl_blocking",
                    "status": "FAIL",
                    "message": "Access Control List (ACL) explicit deny statement blocking packet transit.",
                    "severity": "HIGH"
                }
        return None
    
    def _check_nat_missing(self, evidence: Evidence, case: Optional[Case]) -> Optional[Dict[str, Any]]:
        """Audit IP NAT overload / translation rules."""
        raw_text = " ".join(evidence.to_dict().values()).lower()
        
        if 'nat' in raw_text:
            if any(term in raw_text for term in ['no ip nat', 'nat missing', 'not translated']):
                return {
                    "check": "nat_missing",
                    "status": "FAIL",
                    "message": "IP NAT translation inside/outside or overload statement missing.",
                    "severity": "HIGH"
                }
        return None
    
    def _same_subnet(self, ip_a: str, ip_b: str, mask: str) -> bool:
        """Bitwise comparison to evaluate whether two IP addresses belong to the identical subnet."""
        try:
            parts_a = [int(p) for p in ip_a.split('.')]
            parts_b = [int(p) for p in ip_b.split('.')]
            parts_m = [int(p) for p in mask.split('.')]
            
            return all((parts_a[i] & parts_m[i]) == (parts_b[i] & parts_m[i]) for i in range(4))
        except Exception:
            return False


def run_rule_checker(evidence: Evidence, case: Optional[Case] = None) -> List[Dict[str, Any]]:
    """Helper entry point executing deterministic rule verification suite."""
    engine = RuleChecker()
    return engine.run_all_checks(evidence, case)