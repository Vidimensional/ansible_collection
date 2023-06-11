# github_releases Ansible Lookup

Lookup release information for a given GitHub repository

## Example usage

```yaml
- name: Get latest Terraform version
  ansible.builtin.debug:
    msg: "{{ lookup('github_release', 'hashicorp/terraform', 'latest'}}"
```
