# Legal Risks Assessment: Forking Unlicensed Code

## Current Situation

This project is a fork of code that currently has **no explicit license**. We have added an MIT License to our fork to clarify that our modifications and the codebase as we use it are available under MIT terms.

## Risk Analysis

### ⚠️ Primary Risks

1. **Upstream License Uncertainty**
   - **Risk**: If the upstream author later adds a restrictive license (e.g., GPL, proprietary), there could be legal ambiguity about what rights you have to code committed before the license change.
   - **Mitigation**: You're tracking upstream closely and have a plan to detach if restrictive terms are added. This is a reasonable approach.

2. **Copyright Ownership**
   - **Risk**: Code without a license is still copyrighted by default (in most jurisdictions). The author retains all rights, meaning technically you need permission to use it.
   - **Mitigation**: Adding MIT to your fork doesn't grant you rights to the original code, but it does clarify the terms for your modifications and derivative work. This is a common practice in open source.

3. **Contributor Rights**
   - **Risk**: If you accept contributions, contributors may have different assumptions about licensing.
   - **Mitigation**: Clear LICENSE file and CONTRIBUTING guidelines can help.

### ✅ Mitigating Factors

1. **Public Repository**
   - The code is publicly available on GitHub, which suggests the author is comfortable with others seeing/using it
   - No explicit prohibition against use

2. **Your Approach**
   - Adding MIT license to your fork is proactive and clear
   - Tracking upstream gives you visibility into changes
   - Plan to detach if terms become restrictive is prudent

3. **Common Practice**
   - Many projects start unlicensed and later add licenses
   - Forking unlicensed code and adding your own license is not uncommon
   - The open source community generally operates on good faith

### 📋 Recommended Actions

1. **Document Your Fork**
   - Keep clear records of what you've modified
   - Maintain a fork relationship acknowledgment in README

2. **Monitor Upstream**
   - Set up GitHub notifications for upstream repository
   - Review license changes promptly

3. **Consider Documentation**
   - Add a note in your README about the fork relationship
   - Document any significant modifications you make

4. **Contribution Guidelines**
   - If you accept contributions, require contributors to acknowledge the licensing situation
   - Consider a Contributor License Agreement (CLA) for larger projects

5. **Legal Review** (if commercial use)
   - If this will be used commercially, consider brief legal review
   - Document your use case and risk tolerance

### 🎯 Risk Level Assessment

**For Personal/Internal Use**: **LOW-MEDIUM RISK**
- Practical risk is low if you're using it internally
- Upstream author would need to assert copyright to create issues
- MIT on your fork protects your modifications

**For Public/Commercial Distribution**: **MEDIUM RISK**
- Higher visibility increases potential for upstream author to assert rights
- Still relatively low risk given public availability and no explicit restrictions
- Your MIT license protects recipients of your fork

**For Critical/Production Systems**: **MEDIUM-HIGH RISK**
- If business-critical, consider reaching out to upstream author for clarification
- Document your decision-making process
- Have a contingency plan to replace or rewrite if needed

## Best Practices Moving Forward

1. **Track Upstream Changes**: Continue monitoring for license additions
2. **Document Modifications**: Keep clear records of what you've changed
3. **Consider Contact**: You might reach out to upstream author to ask about licensing intentions (low-pressure, friendly inquiry)
4. **Be Prepared to Detach**: If restrictive terms appear, be ready to remove upstream code and maintain only your modifications

## Conclusion

Adding an MIT license to your fork is a reasonable and proactive step. The primary risk is uncertainty about upstream author's intentions, but this is mitigated by:
- The code being publicly available
- Your plan to track and detach if needed
- Your clear documentation of terms

The risk is generally **low to moderate** depending on your use case, and your approach of adding MIT and tracking upstream is a sensible strategy.

---

**Disclaimer**: This is not legal advice. For formal legal counsel, consult with an attorney familiar with software licensing and intellectual property law.





